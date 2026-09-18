// Shell identity shared by health/ready routes.
// Keep this free of domain concepts: no workspace, incident, user, or action fields.
export const SHELL_SERVICE = "web" as const;
export const SHELL_VERSION = process.env.NERVEOPS_SHELL_VERSION ?? "0.1.0-m0-01";

const BOOT_TIME = Date.now();

export function shellStatus() {
  return {
    status: "ok" as const,
    service: SHELL_SERVICE,
    version: SHELL_VERSION,
    uptimeSeconds: Math.floor((Date.now() - BOOT_TIME) / 1000)
  };
}
