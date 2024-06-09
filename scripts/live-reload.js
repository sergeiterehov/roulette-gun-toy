// @ts-check

const fs = require("fs");
const path = require("path");
const cp = require("child_process");

/*
Этот скрипт делает live reload кода на платке.

-p PORT
*/

const args = {};

for (let i = 0; i < process.argv.length; i += 1) {
  if (process.argv[i].startsWith("-")) {
    args[process.argv[i].substring(1)] = process.argv[i + 1]
  }
}

const cwd = process.cwd()
const port = args.port || "/dev/cu.usbmodem1234561"

const delay = (ms, signal) => new Promise((resolve, reject) => {
  if (signal?.aborted) {
    throw signal.reason
  }

  const timer = setTimeout(resolve, ms)

  signal?.addEventListener("abort", () => {
    clearTimeout(timer)
    reject()
  })
})

const exec = async (command, signal) => {
  if (signal?.aborted) {
    throw signal.reason
  }

  const proc = cp.exec(command)

  signal?.addEventListener("abort", () => proc.kill(9))

  proc.stdout?.on("data", (b) => process.stdout.write(b))
  proc.stderr?.on("data", (b) => process.stderr.write(b))

  if (!proc.killed) {
    await new Promise((resolve, reject) => proc.once("exit", (c) => c !== 0 ? reject() : resolve(undefined)))
  }
}

const run = async (signal) => {
  console.log("Running...")

  await exec(`ampy -p ${port} run boot.py`, signal)
}

const reset = async (signal) => {
  console.log("Resetting...")

  await exec(`ampy -p ${port} reset`, signal)

  console.log("RESET")
}

const upload = async (filepath, signal) => {
  console.log("Uploading...")

  try {
    await exec(`ampy -p ${port} put ${filepath}`, signal)

    console.log(`UPLOADED`)
  } catch (e) {
    console.error(`UPLOADING !ERROR!: ${e}`);
    throw e
  }
}

const remove = async (filename, signal) => {
  console.log("Removing!!!")

  try {
    await exec(`ampy -p ${port} rm ${filename}`, signal)

    console.log(`REMOVED`)
  } catch (e) {
    console.error(`REMOVING !ERROR!: ${e}`);
    throw e
  }
}

console.clear();
console.log(`DEVICE ${port}`);
console.log(`WATCHING ${cwd} ...`);

/** @type {{ action: "changed"|"created"|"removed", filepath: string }[]} */
let queue = [];
let next = Promise.resolve()
let abort = new AbortController()

const consume = async () => {
  const event = queue.shift()

  if (!event) {
    return;
  }

  const { action, filepath } = event;
  const filename = path.basename(filepath);

  try {
    console.log(`[${action}] ${filename}`);

    // Это отменить нельзя!
    if (action === "changed" || action === "created") {
      await upload(filepath)
    } else if (action === "removed") {
      await remove(filename)
    }
  } catch (e) {
    console.log("ABORTED!")
  }

  if (!queue.length) {
    try {
      await delay(1000, abort.signal)

      console.clear();

      await run(abort.signal)
    } catch (e) {
      console.log("ABORTED!")
    }
  }
}

fs.watch(cwd, async (eventType, filename) => {
  if (!filename || !filename.endsWith(".py") || filename.endsWith(".host.py")) return;

  const filepath = path.join(cwd, filename);
  const exists = fs.existsSync(filepath);
  const action = eventType === "change" ? "changed" : exists ? "created" : "removed";

  console.log(`[action detected: ${action}]`);

  if (!abort.signal.aborted) {
    abort.abort();
  }

  abort = new AbortController()

  for (let i = 0; i < queue.length; i += 1) {
    if (queue[i].action === action && queue[i].filepath === filepath) {
      queue.splice(i, 1);
      break;
    }
  }

  if (!queue.length) {
    next = next.finally(async () => {
      try {
        await reset()
      } catch (e) {
        console.error(`RESET ERROR: ${e}`)
      }
    });
  }

  queue.push({ action, filepath });

  next = next.finally(consume);
})