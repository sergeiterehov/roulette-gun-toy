const fs = require("fs");
const path = require("path");
const cp = require("child_process");

/*
Этот скрипт делает live reload кода на платке.

-p PORT
*/

const args = {};

for (let i = 0; i < process.argv; i += 1) {
  if (process.argv[i].startsWith("-")) {
    args[process.argv[i].substring(1)] = process.argv[i + 1]
  }
}

const cwd = process.cwd()
const port = args.port || "/dev/cu.usbmodem1234561"

let abort = new AbortController()

const run = () => {
  if (!abort.signal.aborted) {
    abort.abort();
  }

  abort = new AbortController()

  const proc = cp.exec(`ampy -p ${port} run boot.py`, { signal: abort.signal })

  proc.stdin.write("\n")

  proc.stdout.on("data", (b) => process.stdout.write(b))
  proc.stderr.on("data", (b) => process.stderr.write(b))
}

const upload = (filepath) => {
  console.log("Uploading...")

  try {
    const res = cp.execSync(`ampy -p ${port} put ${filepath}`)
    console.log(`UPLOADING RESULT: ${res.toString("utf8")}`)
  } catch (e) {
    console.error(`UPLOADING !ERROR!:`);
  }
}

const remove = (filename) => {
  console.log("Removing!!!")

  try {
    const res = cp.execSync(`ampy -p ${port} rm ${filename}`)
    console.log(`REMOVING RESULT: ${res.toString("utf8")}`)
  } catch (e) {
    console.error(`REMOVING !ERROR!`);
  }
}

console.clear();
console.log(`DEVICE ${port}`);
console.log(`WATCHING ${cwd} ...`);

fs.watch(cwd, (eventType, filename) => {
  if (!filename.endsWith(".py") || filename.endsWith(".host.py")) return;

  const filepath = path.join(cwd, filename);
  const exists = fs.existsSync(filepath);

  const action = eventType === "change" ? "changed" : exists ? "removed" : "created";

  console.clear();
  console.log(`[${action}] ${filename}`);

  if (action === "changed" || action === "created") {
    upload(filepath)
  } else if (action === "removed") {
    remove(filename)
  }

  run()
})