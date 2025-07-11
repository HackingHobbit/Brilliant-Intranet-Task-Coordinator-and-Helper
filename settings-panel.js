document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('settings-btn');
  const panel = document.getElementById('settings-panel');
  btn.addEventListener('click', () => {
    panel.classList.toggle('hidden');
    panel.innerHTML = `
      <h2>Settings</h2>
      <form id="config-form">
        <label>Email Mode: <select name="email_mode"><option value="local">Local</option><option value="gmail">Gmail</option><option value="outlook">Outlook</option><option value="icloud">iCloud</option></select></label>
        <label>Calendar Mode: <select name="calendar_mode"><option value="local">Local</option><option value="gmail">Gmail</option><option value="outlook">Outlook</option><option value="icloud">iCloud</option></select></label>
        <label>Financial API: <select name="financial_api"><option value="yfinance">yfinance</option><option value="alpha_vantage">Alpha Vantage</option><option value="finnhub">Finnhub</option></select></label>
        <label>Enable 3D: <input type="checkbox" name="enable_3d"></label>
        <button type="submit">Save</button>
      </form>
    `;
    document.getElementById('config-form').addEventListener('submit', e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(e.target));
      axios.post('http://localhost:5000/update_config', data).then(() => {
        panel.classList.add('hidden');
      });
    });
  });
});