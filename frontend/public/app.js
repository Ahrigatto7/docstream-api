
let uploadFiles = {};

function showSection(name) {
  document.querySelectorAll('.section').forEach(sec => sec.classList.add('hidden'));
  document.getElementById(name).classList.remove('hidden');
}

document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const fileInput = document.getElementById("file");
  const file = fileInput.files[0];

  if (file) {
    const fileName = file.name;
    const fileUrl = URL.createObjectURL(file);
    uploadFiles[fileName] = fileUrl;

    let text = "";
    if (file.name.endsWith(".txt")) {
      text = await file.text();
    } else if (file.name.endsWith(".pdf")) {
      text = await extractTextFromPDF(file);
    } else {
      document.getElementById("uploadResult").textContent = "⚠️ .txt/.pdf만 지원됩니다.";
      return;
    }

    const tags = extractTags(text);
    saveUploadRecord(fileName, tags);
    postToServer(fileName, text, tags);

    displayUploadHistory();
    document.getElementById("uploadResult").textContent = `✅ "${file.name}" 업로드 및 저장 완료`;
    fileInput.value = "";
  }
});

async function extractTextFromPDF(file) {
  const pdfjsLib = window['pdfjs-dist/build/pdf'];
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.worker.min.js';
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  let fullText = '';

  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    const page = await pdf.getPage(pageNum);
    const content = await page.getTextContent();
    const strings = content.items.map(item => item.str);
    fullText += strings.join(' ') + ' ';
  }

  return fullText;
}

function extractTags(text) {
  const keywords = {
    "虛透": ["虛透", "허투"],
    "帶象": ["帶象", "대상"],
    "墓庫": ["墓庫", "묘고"],
    "殺星": ["殺星", "살성"],
    "格局": ["格局", "격국"]
  };

  const foundTags = new Set();
  const lowered = text.toLowerCase();

  for (const [key, variants] of Object.entries(keywords)) {
    if (variants.some(v => lowered.includes(v.toLowerCase()))) {
      foundTags.add(key);
    }
  }

  return Array.from(foundTags);
}

function saveUploadRecord(fileName, tags) {
  let history = JSON.parse(localStorage.getItem("uploadHistory")) || [];
  history.unshift({ fileName, tags });
  localStorage.setItem("uploadHistory", JSON.stringify(history));
}

function postToServer(fileName, content, tags) {
  fetch("http://localhost:3000/api/upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fileName, content, tags })
  }).then(res => res.json())
    .then(data => {
      if (!data.success) console.error("서버 저장 실패:", data.error);
    });
}

function deleteUpload(index) {
  let history = JSON.parse(localStorage.getItem("uploadHistory")) || [];
  const removed = history.splice(index, 1)[0];

  if (uploadFiles[removed.fileName]) {
    URL.revokeObjectURL(uploadFiles[removed.fileName]);
    delete uploadFiles[removed.fileName];
  }

  localStorage.setItem("uploadHistory", JSON.stringify(history));
  displayUploadHistory();
}

function displayUploadHistory() {
  const historyList = document.getElementById("uploadHistoryList");
  historyList.innerHTML = "";

  const history = JSON.parse(localStorage.getItem("uploadHistory")) || [];

  history.forEach((entry, index) => {
    const li = document.createElement("li");

    const link = document.createElement("a");
    link.href = uploadFiles[entry.fileName] || "#";
    link.download = entry.fileName;
    link.textContent = entry.fileName;
    link.style.marginRight = "10px";

    const tagSpans = (entry.tags || []).map(tag => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = tag;
      return span;
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "❌";
    deleteBtn.onclick = () => deleteUpload(index);

    li.appendChild(link);
    tagSpans.forEach(tag => li.appendChild(tag));
    li.appendChild(deleteBtn);
    historyList.appendChild(li);
  });
}

document.addEventListener("DOMContentLoaded", displayUploadHistory);
