import { Controller, Get } from "@nestjs/common";
import { shellStatus } from "./shell";

// M0-01 operability probes only. No domain data, no authority-changing operation.
// Blueprint §57: Control Plane never owns run state, leases/fences,
// evidence/truth revisions, action execution, reconciliation, or verification.
@Controller()
export class HealthController {
  @Get("health")
  health() {
    return shellStatus();
  }

  @Get("ready")
  ready() {
    // M0-01 readiness = shell can serve. #3 owns infra-gated readiness.
    return { ...shellStatus(), ready: true };
  }
}
