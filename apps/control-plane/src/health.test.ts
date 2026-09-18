import { describe, expect, it } from "vitest";
import { shellStatus } from "./health/shell";

// M0-01 shell operability contract: health shape only, no domain leakage.
describe("control-plane shell operability", () => {
  it("exposes only shell-operability fields", () => {
    const body = shellStatus();
    expect(body.status).toBe("ok");
    expect(body.service).toBe("control-plane");
    expect(typeof body.version).toBe("string");
    expect(typeof body.uptimeSeconds).toBe("number");
    expect(Object.keys(body).sort()).toEqual(["service", "status", "uptimeSeconds", "version"]);
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
