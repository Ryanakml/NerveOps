import { describe, expect, it } from "vitest";
import { SHELL_SERVICE, shellStatus } from "./app/lib-shell";

// M0-01 shell operability contract: health shape only, no domain leakage.
describe("web shell operability", () => {
  it("exposes only shell-operability fields", () => {
    const body = shellStatus();
    expect(body.status).toBe("ok");
    expect(body.service).toBe(SHELL_SERVICE);
    expect(typeof body.version).toBe("string");
    expect(typeof body.uptimeSeconds).toBe("number");
    const keys = Object.keys(body).sort();
    expect(keys).toEqual(["service", "status", "uptimeSeconds", "version"]);
  });

  it("exposes no domain-owned fields", () => {
    const raw = JSON.stringify(shellStatus()).toLowerCase();
    for (const forbidden of [
      "workspace",
      "incident",
      "hypothesis",
      "evidence",
      "approval",
      "intent",
      "execution",
      "lease",
      "policy"
    ]) {
      expect(raw).not.toContain(forbidden);
    }
  });
});
