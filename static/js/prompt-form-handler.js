// ./js/login_validation.js
(function () {
  const form = document.getElementById("promptForm");
  const promptInput = document.getElementById("prompt");
  const errorMsg = document.getElementById("errorMsg");
  const submitBtn = form?.querySelector('button[type="submit"]');

  if (!form || !promptInput || !errorMsg) {
    console.error("必要な要素が見つかりません。HTMLのidを確認してください。");
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault(); // 既定のフォーム送信は止める（JSON送信するため）

    const prompt = promptInput.value.trim();
    errorMsg.textContent = "";

    // フロント側の簡易バリデーション
    if (!prompt) {
      errorMsg.textContent = "プロンプトを入力してください。";
      return;
    }

    // 二重送信防止
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "送信中...";
    }

    try {
      const response = await fetch("/prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin", // 同一オリジンのCookie送信/受信
        body: JSON.stringify({ prompt }),
      });

      // サーバーからのメッセージを拾う（可能なら）
      let data = null;
      try {
        data = await response.json();
      } catch (_) {
        // JSONでない場合もあるので無視
      }

      if (!response.ok) {
        // 401（認証失敗）/500（内部エラー）など
        let msg = "サーバーエラーが発生しました。";
        if (data) {
          msg = data.message || data.answer || msg;
        }
        throw new Error(msg);
      }

      answerBox.textContent =
        (data && (data.answer || data.message)) || "回答がありません";
    } catch (err) {
      console.error(err);
      errorMsg.textContent = err.message || "処理に失敗しました。";
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "送信";
      }
    }
  });
})();
