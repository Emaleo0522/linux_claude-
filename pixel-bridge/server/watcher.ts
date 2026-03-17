import { watch } from "chokidar";
import { statSync, readdirSync, openSync, readSync, closeSync } from "fs";
import { join, basename, dirname } from "path";
import { homedir } from "os";
import { EventEmitter } from "events";

const CLAUDE_PROJECTS_DIR = join(homedir(), ".claude", "projects");
const ACTIVE_THRESHOLD_MS = 600_000; // 10 minutes — Claude can think for 5+ min without writing
const POLL_INTERVAL_MS = 1000;

export interface WatchedFile {
  path: string;
  sessionId: string;
  projectName: string;
  offset: number;
  lineBuffer: string;
}

export class JsonlWatcher extends EventEmitter {
  private files = new Map<string, WatchedFile>();
  private watcher: ReturnType<typeof watch> | null = null;
  private pollInterval: ReturnType<typeof setInterval> | null = null;

  start(): void {
    this.scanForActiveFiles();

    this.watcher = watch(CLAUDE_PROJECTS_DIR, {
      ignoreInitial: true,
      depth: 3,
      usePolling: true,
      interval: 1000,
    });

    this.watcher.on("add", (filePath: string) => {
      if (filePath.endsWith(".jsonl")) {
        this.addFile(filePath);
      }
    });

    // When a file is deleted, remove it from tracking so a subsequent
    // "add" (recreate) is handled cleanly with offset reset to 0.
    this.watcher.on("unlink", (filePath: string) => {
      const file = this.files.get(filePath);
      if (file) {
        this.files.delete(filePath);
        this.emit("fileRemoved", file);
      }
    });

    this.pollInterval = setInterval(() => this.pollFiles(), POLL_INTERVAL_MS);
  }

  stop(): void {
    this.watcher?.close();
    if (this.pollInterval) clearInterval(this.pollInterval);
  }

  private scanForActiveFiles(): void {
    try {
      const dirs = readdirSync(CLAUDE_PROJECTS_DIR, { withFileTypes: true });
      for (const dir of dirs) {
        if (!dir.isDirectory()) continue;
        const dirPath = join(CLAUDE_PROJECTS_DIR, dir.name);
        try {
          const files = readdirSync(dirPath);
          for (const f of files) {
            if (!f.endsWith(".jsonl")) continue;
            const filePath = join(dirPath, f);
            const stat = statSync(filePath);
            if (Date.now() - stat.mtimeMs < ACTIVE_THRESHOLD_MS) {
              this.addFile(filePath);
            }
          }
        } catch {
          /* skip unreadable dirs */
        }
      }
    } catch {
      /* projects dir may not exist */
    }
  }

  private addFile(filePath: string): void {
    if (this.files.has(filePath)) return;

    const sessionId = basename(filePath, ".jsonl");
    const projectDirName = basename(dirname(filePath));
    // Extract short project name: "-Users-alice-Documents-myproject-657" -> "myproject"
    // Walk backwards, skipping purely numeric trailing segments (e.g. version/port numbers).
    const parts = projectDirName.split("-").filter(Boolean);
    let projectName = sessionId.slice(0, 8);
    for (let i = parts.length - 1; i >= 0; i--) {
      if (!/^\d+$/.test(parts[i])) {
        projectName = parts[i];
        break;
      }
    }

    const file: WatchedFile = {
      path: filePath,
      sessionId,
      projectName,
      offset: 0,
      lineBuffer: "",
    };

    this.files.set(filePath, file);
    this.emit("fileAdded", file);

    // Read existing content to catch up
    this.readNewLines(file);
  }

  private pollFiles(): void {
    for (const [path, file] of this.files) {
      try {
        const stat = statSync(path);
        if (stat.size > file.offset) {
          this.readNewLines(file);
        }
        // Remove stale files
        if (Date.now() - stat.mtimeMs > ACTIVE_THRESHOLD_MS) {
          this.files.delete(path);
          this.emit("fileRemoved", file);
        }
      } catch {
        this.files.delete(path);
        this.emit("fileRemoved", file);
      }
    }
  }

  private readNewLines(file: WatchedFile): void {
    try {
      const stat = statSync(file.path);
      if (stat.size <= file.offset) return;

      const buf = Buffer.alloc(stat.size - file.offset);
      const fd = openSync(file.path, "r");
      readSync(fd, buf, 0, buf.length, file.offset);
      closeSync(fd);

      file.offset = stat.size;
      const text = file.lineBuffer + buf.toString("utf-8");
      const lines = text.split("\n");

      // Last element is incomplete line (buffer it)
      file.lineBuffer = lines.pop() || "";

      for (const line of lines) {
        if (line.trim()) {
          this.emit("line", file, line);
        }
      }
    } catch {
      /* file may have been deleted */
    }
  }

  getActiveFiles(): WatchedFile[] {
    return Array.from(this.files.values());
  }
}
