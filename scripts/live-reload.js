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

const delay = (ms, signal) => new Promise((resolve, reject) => {
  const timer = setTimeout(resolve, ms)

  signal.addEventListener("abort", () => {
    clearTimeout(timer)
    reject()
  })
})

const exec = async (command, signal) => {
  const proc = cp.exec(command)

  signal.addEventListener("abort", () => proc.kill(9))

  proc.stdout.on("data", (b) => process.stdout.write(b))
  proc.stderr.on("data", (b) => process.stderr.write(b))

  if (!proc.killed) {
    await new Promise((resolve, reject) => proc.once("exit", (c) => c ? reject() : resolve()))
  }
}

const run = async (signal) => {
  console.log("Running...")

  await exec(`ampy -p ${port} run boot.py`, signal)
}

const upload = async (filepath, signal) => {
  console.log("Uploading...")

  try {
    await exec(`ampy -p ${port} put ${filepath}`, signal)

    console.log(`UPLOADED`)
  } catch (e) {
    console.error(`UPLOADING !ERROR!:`);
    throw e
  }
}

const remove = async (filename, signal) => {
  console.log("Removing!!!")

  try {
    await exec(`ampy -p ${port} rm ${filename}`, sinal)

    console.log(`REMOVED`)
  } catch (e) {
    console.error(`REMOVING !ERROR!`);
    throw e
  }
}

console.clear();
console.log(`DEVICE ${port}`);
console.log(`WATCHING ${cwd} ...`);

let abort = new AbortController()

fs.watch(cwd, async (eventType, filename) => {
  if (!filename.endsWith(".py") || filename.endsWith(".host.py")) return;

  if (!abort.signal.aborted) abort.abort();

  console.log(`[action detected]`);

  abort = new AbortController()

  try {
    await delay(1000, abort.signal)

    const filepath = path.join(cwd, filename);
    const exists = fs.existsSync(filepath);

    const action = eventType === "change" ? "changed" : exists ? "removed" : "created";

    console.clear();
    console.log(`[${action}] ${filename}`);

    if (action === "changed" || action === "created") {
      await upload(filepath, abort.signal)
    } else if (action === "removed") {
      await remove(filename, abort.signal)
    }

    await run(abort.signal)
  } catch (e) {
    console.log("ABORTED!")
  }
})