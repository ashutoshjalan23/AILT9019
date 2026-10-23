const $ = (id) => document.getElementById(id);
const form = $('chat-form');
let busy = false;
let lastBuilding = '';
function paragraph(text, className) { const p = document.createElement('p'); p.textContent = text; if (className) p.className = className; return p; }
function addMessage(text, who) { $('conversation').append(paragraph(text, who)); $('conversation').scrollTop = $('conversation').scrollHeight; }
async function request(path, payload) {
  const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed. Please try again.');
  return data;
}
function setBusy(value) {
  busy = value; ['send','reset','now','building','clock','message'].forEach(id => $(id).disabled = value);
  $('send').textContent = value ? 'Checking options…' : 'Find food';
  $('results').setAttribute('aria-busy', String(value));
}
function render(data) {
  $('results').replaceChildren();
  const labels = {building:v=>v, diet:v=>v, cuisine:v=>v, budget:v=>`Up to HK$${v}`, time_limit:v=>`${v} min break`, spicy:v=>v?'Spicy':'No spicy tag', quiet:v=>v?'Quiet':'No quiet tag', clock:v=>`At ${v}`};
  $('filters').textContent = Object.entries(data.context).map(([k,v]) => labels[k] ? labels[k](v) : '').filter(Boolean).join(' · ') || 'No preferences yet.';
  $('evaluated').textContent = `Checked at ${data.at.slice(0,16).replace('T',' ')} (Hong Kong)`;
  $('mode').textContent = data.mode === 'bailian' ? 'Bailian model + fixed-data filters' : data.mode === 'hybrid' ? 'Model parsing + offline ranking' : 'Offline rules demo';
  if (data.notice) $('mode').textContent += '. ' + data.notice;
  if (!data.recommendations.length) $('results').append(paragraph(data.message, 'empty'));
  for (const item of data.recommendations) {
    const article = document.createElement('article'); article.className = 'option';
    const heading = document.createElement('h3'); heading.textContent = item.name; article.append(heading);
    article.append(paragraph(`HK$${item.price_min}–${item.price_max} · ${item.walk_minutes} min walk`, 'meta'));
    article.append(paragraph(`${item.building} · Floor ${item.floor}`, 'detail'));
    article.append(paragraph(item.reason));
    if (item.model_reason) article.append(paragraph('Model explanation: ' + item.model_reason, 'detail'));
    article.append(paragraph(item.walk_minutes === 0 ? 'You are in the same building. Find the listed floor.' : 'Illustrative route: ' + item.route, 'detail'));
    article.append(paragraph(item.tip, 'detail')); $('results').append(article);
  }
  if (data.context.building) { $('building').value = data.context.building; lastBuilding = data.context.building; }
}
form.addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  const message = $('message').value.trim(); if (!message) return;
  const building = $('building').value;
  const text = building && building !== lastBuilding ? `I'm at ${building}. ${message}` : message;
  $('error').textContent = ''; setBusy(true); addMessage(text, 'user');
  // Remove obsolete options while a new request is pending or has failed.
  $('results').replaceChildren(paragraph('Checking demo options…', 'empty'));
  try { const data = await request('/api/chat', {message:text, at:$('clock').value || undefined}); render(data); addMessage(data.message, 'assistant'); $('message').value = ''; }
  catch (error) { $('error').textContent = error.message; $('results').replaceChildren(paragraph('No current results. Please try again.', 'empty')); }
  finally { setBusy(false); $('message').focus(); }
});
$('now').addEventListener('click', () => { $('clock').value = new Date(Date.now() + 8*3600000).toISOString().slice(0,16); });
$('reset').addEventListener('click', async () => {
  if (busy) return; setBusy(true);
  try { await request('/api/reset', {}); lastBuilding = ''; $('building').value = ''; $('message').value = ''; $('error').textContent = ''; $('filters').textContent = 'Your preferences will appear here.'; $('evaluated').textContent = ''; $('results').replaceChildren(paragraph('Choose a building and send a request.', 'empty')); $('conversation').replaceChildren(paragraph('New chat started. Where are you starting from?', 'assistant')); }
  catch(error) { $('error').textContent = error.message; } finally { setBusy(false); }
});
fetch('/api/status').then(r => { if(!r.ok) throw new Error(); return r.json(); }).then(data => {
  for(const building of data.buildings) { const option = document.createElement('option'); option.value = option.textContent = building; $('building').append(option); }
  $('mode').textContent = data.model_configured ? 'Bailian enabled; connection checked on request' : 'Offline rules demo';
}).catch(() => { $('mode').textContent = 'Connection unavailable'; $('error').textContent = 'Cannot reach the local server. Reload the page after starting it.'; });
