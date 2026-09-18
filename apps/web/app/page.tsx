// M0-01 Web Product shell.
// Blueprint §56: owns workspace UX surface only. Never owns authorization,
// approval validity, incident truth, action state, or execution authority.
// This page is a composable placeholder; M3 owns the real Incident Workspace.

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-6 p-8">
      <p className="text-xs uppercase tracking-widest text-neutral-400">NerveOps · M0-01 shell</p>
      <h1 className="text-3xl font-semibold">Web Product shell is running</h1>
      <p className="text-sm leading-6 text-neutral-300">
        This is a role boundary and process entrypoint only. It contains no workspace, incident,
        evidence, approval, or remediation behavior. Operability probes live at{" "}
        <code className="rounded bg-neutral-800 px-1">/api/health</code> and{" "}
        <code className="rounded bg-neutral-800 px-1">/api/ready</code>.
      </p>
      <ul className="list-disc pl-5 text-sm text-neutral-400">
        <li>Blueprint §§54–56, 103–106, 124 apply; M1/M2 behavior is a non-goal.</li>
        <li>Browser refresh reconstructs from durable API state (future M3).</li>
        <li>See repository docs for layout, commands, and config contract.</li>
      </ul>
    </main>
  );
}
