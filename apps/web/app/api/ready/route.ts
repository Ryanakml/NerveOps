import { NextResponse } from "next/server";
import { shellStatus } from "../../lib-shell";

// M0-01 readiness = shell can serve traffic. It intentionally does NOT gate on
// PostgreSQL/Redis/model state; #3 owns infrastructure readiness wiring.
export async function GET() {
  return NextResponse.json({ ...shellStatus(), ready: true }, { status: 200 });
}
