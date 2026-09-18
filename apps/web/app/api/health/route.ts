import { NextResponse } from "next/server";
import { shellStatus } from "../../lib-shell";

// M0-01 operability probe only. Exposes no domain data and performs no
// authority-changing operation (issue acceptance contract).
export async function GET() {
  return NextResponse.json(shellStatus(), { status: 200 });
}
