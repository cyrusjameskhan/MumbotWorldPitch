const COOKIE_NAME = "mumbot_world_gate";
const COOKIE_VALUE = "granted";
const PASSWORD = Deno.env.get("MUMBOT_SITE_PASSWORD") || "gamefromtheforestfloor";

function hasAccess(request: Request): boolean {
  const cookie = request.headers.get("cookie") || "";
  return cookie
    .split(";")
    .map((part) => part.trim())
    .some((part) => part === `${COOKIE_NAME}=${COOKIE_VALUE}`);
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;",
    };
    return entities[char];
  });
}

function gatePage(next: string, failed = false): Response {
  const escapedNext = escapeHtml(next);
  const message = failed ? `<p class="error">That password did not work.</p>` : "";

  return new Response(`<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Mumbot World</title>
    <style>
      :root {
        color-scheme: dark;
        --ink: #100d0a;
        --cream: #f7eccb;
        --parchment: #d6c599;
        --ember: #f05a28;
      }
      * { box-sizing: border-box; }
      body {
        min-height: 100vh;
        margin: 0;
        display: grid;
        place-items: center;
        background:
          radial-gradient(circle at 50% 18%, rgba(240,90,40,0.14), transparent 34%),
          linear-gradient(180deg, #17130f 0%, #050403 100%);
        color: var(--cream);
        font-family: Georgia, "Times New Roman", serif;
      }
      main {
        width: min(460px, calc(100vw - 40px));
        border: 1px solid rgba(247,236,203,0.18);
        background: rgba(16,13,10,0.82);
        padding: 34px;
        box-shadow: 0 28px 70px rgba(0,0,0,0.42);
      }
      .eyebrow {
        margin-bottom: 14px;
        color: var(--ember);
        font: 700 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        letter-spacing: 0.28em;
        text-transform: uppercase;
      }
      h1 {
        margin: 0 0 18px;
        font-size: clamp(38px, 8vw, 64px);
        line-height: 0.92;
        letter-spacing: 0.02em;
      }
      p {
        margin: 0 0 24px;
        color: var(--parchment);
        font-size: 17px;
        line-height: 1.45;
      }
      label {
        display: block;
        margin-bottom: 10px;
        color: var(--parchment);
        font: 700 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }
      input {
        width: 100%;
        height: 48px;
        border: 1px solid rgba(247,236,203,0.28);
        border-radius: 0;
        background: rgba(247,236,203,0.08);
        color: var(--cream);
        padding: 0 14px;
        font: 18px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        outline: none;
      }
      input:focus { border-color: var(--ember); }
      button {
        width: 100%;
        height: 48px;
        margin-top: 14px;
        border: 0;
        border-radius: 0;
        background: var(--ember);
        color: #160c08;
        cursor: pointer;
        font: 800 12px/1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        letter-spacing: 0.22em;
        text-transform: uppercase;
      }
      .error {
        margin: -8px 0 18px;
        color: #ff9b75;
        font: 700 13px/1.3 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }
    </style>
  </head>
  <body>
    <main>
      <div class="eyebrow">Private preview</div>
      <h1>Mumbot World</h1>
      <p>Enter the password to open the pitch deck.</p>
      ${message}
      <form method="post" action="/__password-gate">
        <input type="hidden" name="next" value="${escapedNext}" />
        <label for="password">Password</label>
        <input id="password" name="password" type="password" autocomplete="current-password" autofocus required />
        <button type="submit">Enter</button>
      </form>
    </main>
  </body>
</html>`, {
    status: 401,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

export default async (request: Request, context: { next: () => Promise<Response> }) => {
  const url = new URL(request.url);

  if (url.pathname === "/__password-gate" && request.method === "POST") {
    const form = await request.formData();
    const password = String(form.get("password") || "");
    const next = String(form.get("next") || "/");

    if (password === PASSWORD) {
      const redirectTo = next.startsWith("/") && !next.startsWith("//") ? next : "/";
      return new Response(null, {
        status: 303,
        headers: {
          "location": redirectTo,
          "set-cookie": `${COOKIE_NAME}=${COOKIE_VALUE}; Path=/; Max-Age=604800; HttpOnly; Secure; SameSite=Lax`,
          "cache-control": "no-store",
        },
      });
    }

    return gatePage(next || "/", true);
  }

  if (hasAccess(request)) {
    return context.next();
  }

  const next = `${url.pathname}${url.search}`;
  return gatePage(next || "/");
};
