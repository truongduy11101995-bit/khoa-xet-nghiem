// =========================================================================
// VERCEL EDGE MIDDLEWARE (middleware.ts)
// Kiểm tra IP Whitelisting ở tầng Edge trước khi request đến Server
// =========================================================================

export const config = {
  matcher: ['/((?!api/health|api/client-ip|static/|_next/|favicon.ico).*)'],
};

export default function middleware(request: Request) {
  const url = new URL(request.url);

  // 1. Kiểm tra Admin Remote Bypass (Cookie hoặc Header)
  const cookieHeader = request.headers.get('cookie') || '';
  if (cookieHeader.includes('admin_bypass_token=')) {
    return; // Cho phép đi tiếp
  }

  const bypassHeader = request.headers.get('x-admin-bypass-key');
  const adminBypassKey = process.env.ADMIN_BYPASS_KEY || 'ThienAn2026@Bypass';
  if (bypassHeader && bypassHeader === adminBypassKey) {
    return; // Cho phép đi tiếp
  }

  // 2. Lấy địa chỉ IP thật của người dùng
  const clientIp =
    request.headers.get('cf-connecting-ip') ||
    request.headers.get('x-real-ip') ||
    request.headers.get('x-forwarded-for')?.split(',')[0].trim() ||
    '127.0.0.1';

  // 3. Đọc danh sách IP Wi-Fi cơ quan từ biến môi trường
  const allowedRulesEnv = process.env.ALLOWED_OFFICE_IPS || '';
  if (!allowedRulesEnv || allowedRulesEnv.includes('*')) {
    return; // Cho phép mọi IP nếu chưa cấu hình
  }

  const allowedRules = allowedRulesEnv.split(',').map((s) => s.trim()).filter(Boolean);

  // 4. Kiểm tra xem IP có thuộc danh sách cho phép không
  let isAllowed = false;
  for (const rule of allowedRules) {
    if (rule === clientIp) {
      isAllowed = true;
      break;
    }
    if (rule.endsWith('.*')) {
      const prefix = rule.slice(0, -2);
      if (clientIp.startsWith(prefix)) {
        isAllowed = true;
        break;
      }
    }
    if (['127.0.0.1', '::1', 'localhost'].includes(clientIp) && ['127.0.0.1', 'localhost', '::1'].includes(rule)) {
      isAllowed = true;
      break;
    }
  }

  if (isAllowed) {
    return; // Hợp lệ -> Cho phép truy cập
  }

  // 5. Nếu là API: Chặn và trả về JSON 403
  if (url.pathname.startsWith('/api/')) {
    return new Response(
      JSON.stringify({
        success: false,
        error_code: 'IP_FORBIDDEN',
        message: 'Truy cập bị từ chối. Vui lòng kết nối đúng mạng Wi-Fi nội bộ của cơ quan để chấm công.',
        client_ip: clientIp,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 403,
        headers: { 'content-type': 'application/json' },
      }
    );
  }

  // 6. Nếu là giao diện Web: Trả về trang thông báo 403 HTML chuẩn bệnh viện
  return new Response(
    `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Truy Cập Bị Từ Chối - Khoa Xét Nghiệm</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }
    .card { background: white; max-width: 500px; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #dc2626; }
    h1 { color: #dc2626; font-size: 20px; margin-bottom: 12px; }
    p { color: #475569; line-height: 1.5; font-size: 14px; margin-bottom: 20px; }
    .ip { background: #fee2e2; color: #991b1b; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-family: monospace; display: inline-block; margin-bottom: 20px; }
    button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>TRUY CẬP BỊ TỪ CHỐI (403)</h1>
    <p>Vui lòng kết nối đúng <strong>mạng Wi-Fi nội bộ của cơ quan</strong> để chấm công.</p>
    <div class="ip">Địa chỉ IP hiện tại: ${clientIp}</div>
    <div>
      <button onclick="location.reload()">Thử Lại Kết Nối</button>
    </div>
  </div>
</body>
</html>`,
    {
      status: 403,
      headers: { 'content-type': 'text/html; charset=utf-8' },
    }
  );
}
