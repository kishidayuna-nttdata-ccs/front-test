(function () {
  const form = document.getElementById('loginForm');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const errorMsg = document.getElementById('errorMsg');
  const submitBtn = form?.querySelector('button[type="submit"]');

  if (!form || !usernameInput || !passwordInput || !errorMsg) {
    console.error('必要な要素が見つかりません。HTMLのidを確認してください。');
    return;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault(); // 既定のフォーム送信は止める

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    errorMsg.textContent = '';

    // フロント側の簡易バリデーション
    if (!username && !password) {
      errorMsg.textContent = 'ユーザー名とパスワードを入力してください。';
      return;
    } else if (!username) {
      errorMsg.textContent = 'ユーザー名を入力してください。';
      return;
    } else if (!password) {
      errorMsg.textContent = 'パスワードを入力してください。';
      return;
    }

    // 二重送信防止
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '送信中...';
    }

    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin', // 同一オリジンのCookie送信/受信
        body: JSON.stringify({ username, password }),
      });

      // サーバーからのメッセージを取得
      let data = null;
      try {
        data = await response.json();
      } catch (_) {
        // JSONでない場合
      }

      if (!response.ok) {
        const msg = data.message;
        throw new Error(msg);
      }

      console.log('ログイン成功:', data)
      window.location.href = '/home';
    } catch (err) {
      console.error(err);
      errorMsg.textContent = err.message || 'ログインに失敗しました。';
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'ログイン';
      }
    }
  });
})();