const documentText = document.getElementById("document-text")!;
const typeBar = <HTMLInputElement>document.getElementById("type-bar");
const timerTime = document.getElementById("timer-time")!;
const languageSelect = <HTMLSelectElement>(
  document.getElementById("language-select")
);

const runDuration = 30;
let in_run: boolean = false;
let run_time: number = runDuration;
let docStr: string = "";
let docStrSeparated: string[] = [];
let wordIndex: number = 0;
let runIntervalId: number = 0;
let runStartTimeStamp: number = 0;
interface Timestamp {
  key: string;
  correct: boolean;
}
let timetable: Map<number, Timestamp> = new Map();

typeBar.addEventListener("input", (e) => {
  if (in_run) {
    const text = typeBar.textContent.trim();
    if (text == docStrSeparated[wordIndex]) {
      typeBar.textContent = "";
      ++wordIndex;
      if (wordIndex >= docStrSeparated.length) {
        fetchNewDoc(languageSelect.value);
      }
      highlight();
    }
  } else {
    startRun(languageSelect.value, e.timeStamp);
  }
});

typeBar.addEventListener("keyup", (e) => {
  if (in_run) {
    const text = typeBar.textContent.trim(),
      correct = docStrSeparated[wordIndex].startsWith(text);
    console.log(
      docStrSeparated[wordIndex],
      text,
      docStrSeparated[wordIndex].startsWith(text)
    );
    timetable.set((e.timeStamp - runStartTimeStamp) / 1000, {
      key: e.key,
      correct,
    });
    typeBar.classList.toggle("incorrect", !correct);
  }
});

typeBar.addEventListener("keydown", (e) => {
  if ((e as any).key == "Enter") {
    e.preventDefault();
  }
});

languageSelect.addEventListener("change", () => {
  endRun(languageSelect.value, false);
});

function startRun(lang: string, time: number) {
  in_run = true;
  runStartTimeStamp = time;
  timetable = new Map();
  runIntervalId = setInterval(() => {
    --run_time;
    timerTime.textContent = String(run_time);
    if (run_time == 0) {
      endRun(lang, true);
    }
  }, 1000);
  highlight();
}

function endRun(lang: string, isLogged: boolean) {
  if (runIntervalId != 0) clearInterval(runIntervalId);
  in_run = false;
  run_time = runDuration;
  timerTime.textContent = String(run_time);
  typeBar.textContent = "";
  typeBar.contentEditable = "false";
  typeBar.classList.remove("incorrect");
  fetchNewDoc(lang);
  if (isLogged) {
    logRun();
    console.log("ran log run");
  }
  console.log("before reset");
  timetable = new Map();
  setTimeout(() => {
    typeBar.contentEditable = "true";
  }, 1000);
}

function logRun() {
  console.log(timetable);
  console.log(JSON.stringify(Array.from(timetable.entries())));
  fetch("/logrun", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(Array.from(timetable.entries())),
  });
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
        break;
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

endRun(languageSelect.value, false);

setInterval(() => {
  console.log(timetable);
}, 1000);
