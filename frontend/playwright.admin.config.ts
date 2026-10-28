import { defineConfig, devices } from '@playwright/test';
export default defineConfig({testDir:'./e2e',testMatch:'admin.spec.ts',workers:1,retries:0,timeout:60000,
  use:{baseURL:'http://127.0.0.1:4180',...devices['Desktop Chrome'],screenshot:'only-on-failure'},
  webServer:[
    {command:process.platform==='win32'?'..\\backend\\.venv\\Scripts\\python.exe -m tests.e2e_admin_server':'../backend/.venv/bin/python -m tests.e2e_admin_server',cwd:'../backend',url:'http://127.0.0.1:9019/health',reuseExistingServer:false,timeout:60000},
    {command:'npm run dev -- --host 127.0.0.1 --port 4180 --strictPort',url:'http://127.0.0.1:4180',env:{VITE_ADMIN_API_TARGET:'http://127.0.0.1:9019'},reuseExistingServer:false,timeout:60000},
  ]});
