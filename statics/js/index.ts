const documentText = document.getElementById("document-text")!;
const typeBar = <HTMLInputElement>document.getElementById("type-bar");
const timerTime = document.getElementById("timer-time")!;
const languageSelect = <HTMLSelectElement>(
  document.getElementById("language-select")
);

let in_run: boolean = false;
let run_time: number = 30;
let docStr: string = "";
let docStrSeparated: string[] = [];
let wordIndex: number = 0;

typeBar.addEventListener("input", () => {
  if (in_run) {
    if (typeBar.textContent.trim() == docStrSeparated[wordIndex]) {
      typeBar.textContent = "";
      ++wordIndex;
      highlight();
      if (wordIndex >= docStrSeparated.length) {
        fetchNewDoc(languageSelect.value);
      }
    }
  } else {
    in_run = true;
    startRun(languageSelect.value);
  }
});

function startRun(lang: string) {
  const interval_id = setInterval(() => {
    --run_time;
    timerTime.textContent = String(run_time);
    if (run_time == 0) {
      clearInterval(interval_id);
      in_run = false;
      run_time = 30;
      timerTime.textContent = String(run_time);
      typeBar.textContent = "";
      fetchNewDoc(lang);
    }
  }, 1000);
  highlight();
}

async function fetchNewDoc(lang: string) {
  const res = await fetch(`/doc?lang=${lang}`);
  docStr = await res.text();
  docStrSeparated = docStr.trim().split(/\s+/);
  wordIndex = 0;
  documentText.textContent = docStr;
}

function highlight() {
  const target = docStrSeparated[wordIndex];
  let prevCount = 0;
  for (let i = 0; i <= wordIndex; i++) {
    if (docStrSeparated[i] == target) {
      ++prevCount;
    }
  }
  let targetStart = 0;
  for (let i = 0; i < docStr.length; ) {
    if (
      docStr.startsWith(target, i) &&
      (i + target.length >= docStr.length ||
        /\s/.test(docStr[i + target.length]))
    ) {
      --prevCount;
      if (prevCount == 0) {
        targetStart = i;
      }
    }
    // skip to the next word
    while (!/\s/.test(docStr[i])) ++i;
    while (/\s/.test(docStr[i])) ++i;
  }
  let targetEnd = targetStart;
  for (; targetEnd < docStr.length; ++targetEnd) {
    if (/\s/.test(docStr[targetEnd])) {
      break;
    }
  }
  let markedEle = document.createElement("mark");
  markedEle.innerText = docStr.slice(targetStart, targetEnd);
  documentText.innerHTML = "";
  documentText.append(document.createTextNode(docStr.slice(0, targetStart)));
  documentText.append(markedEle);
  documentText.append(document.createTextNode(docStr.slice(targetEnd)));
}

fetchNewDoc(languageSelect.value);
