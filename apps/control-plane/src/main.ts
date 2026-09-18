import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { logger: ["log", "warn", "error"] });
  app.enableShutdownHooks();
  const webOrigin = process.env.WEB_BASE_URL ?? "http://localhost:3100";
  app.enableCors({ origin: webOrigin });
  const port = Number(process.env.CONTROL_PLANE_PORT ?? 3001);
  await app.listen(port);
  console.log(`control-plane shell listening on :${port}`);
}

void bootstrap();
