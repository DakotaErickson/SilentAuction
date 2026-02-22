const BASE   = window.location.origin;
const WS_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`;

// ── State ──────────────────────────────────────────────────────
const items = new Map(); // item_id → item object

// ── WebSocket ──────────────────────────────────────────────────
let ws;

function connectWS() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    document.getElementById('ws-dot').className = 'ws-dot connected';
    document.getElementById('ws-label').textContent = 'Live';
  };

  ws.onclose = () => {
    document.getElementById('ws-dot').className = 'ws-dot disconnected';
    document.getElementById('ws-label').textContent = 'Reconnecting…';
    setTimeout(connectWS, 3000);
  };

  ws.onerror = () => ws.close();

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleBidUpdate(data);
  };
}

function handleBidUpdate({ item_id, current_bid, item_name }) {
  const item = items.get(item_id);
  if (!item) return;

  item.current_bid = current_bid;

  const priceEl = document.getElementById(`price-${item_id}`);
  if (priceEl) {
    priceEl.textContent = formatCurrency(current_bid);
    priceEl.classList.add('updated');
    setTimeout(() => priceEl.classList.remove('updated'), 1500);
  }

  const hintEl = document.getElementById(`hint-${item_id}`);
  if (hintEl) {
    hintEl.textContent = `Minimum next bid: ${formatCurrency(current_bid + 5)}`;
  }

  const amountInput = document.getElementById(`amount-${item_id}`);
  if (amountInput) {
    amountInput.placeholder = (current_bid + 5).toFixed(2);
  }

  const card = document.getElementById(`card-${item_id}`);
  if (card) {
    card.classList.remove('bid-flash');
    void card.offsetWidth; // force reflow to restart animation
    card.classList.add('bid-flash');
  }

  showToast(`🏆 New bid on "${item_name}": ${formatCurrency(current_bid)}`, 'info');
}

// ── Fetch Items ────────────────────────────────────────────────
async function loadItems() {
  try {
    const res  = await fetch(`${BASE}/items`);
    const data = await res.json();

    document.getElementById('loading').style.display = 'none';

    if (!data.length) {
      document.getElementById('empty').style.display = 'block';
      return;
    }

    data.forEach(item => {
      items.set(item.id, item);
      renderCard(item);
    });
  } catch (err) {
    document.getElementById('loading').innerHTML =
      '<p style="color:var(--error)">Failed to load items. Please refresh.</p>';
  }
}

// ── Render Card ────────────────────────────────────────────────
function renderCard(item) {
  const grid    = document.getElementById('items-grid');
  const minNext = formatCurrency(item.current_bid + 5);

  const card = document.createElement('div');
  card.className = 'item-card';
  card.id = `card-${item.id}`;

  card.innerHTML = `
    <div class="card-accent"></div>
    <div class="card-body">
      <div class="item-number">Item #${String(item.id).padStart(2, '0')}</div>
      <div class="item-name">${escHtml(item.name)}</div>
      <div class="item-description">${escHtml(item.description)}</div>

      <div class="bid-section">
        <div class="bid-row">
          <div>
            <div class="bid-label">Current Bid</div>
            <div class="current-bid" id="price-${item.id}">${formatCurrency(item.current_bid)}</div>
          </div>
          <div style="text-align:right">
            <div class="starting-bid">Starts at ${formatCurrency(item.starting_bid)}</div>
            <div class="min-increment" id="hint-${item.id}">Minimum next bid: ${minNext}</div>
          </div>
        </div>

        <form class="bid-form" onsubmit="submitBid(event, ${item.id})">
          <div class="input-row">
            <div class="input-wrap">
              <span class="input-prefix">$</span>
              <input
                type="number"
                id="amount-${item.id}"
                placeholder="${(item.current_bid + 5).toFixed(2)}"
                min="${(item.current_bid + 5).toFixed(2)}"
                step="0.01"
                required
                aria-label="Bid amount"
              />
            </div>
            <button type="submit" class="btn-bid" id="btn-${item.id}">Place Bid</button>
          </div>
          <input
            type="text"
            id="contact-${item.id}"
            placeholder="Email or phone number"
            required
            aria-label="Email or phone"
          />
          <div class="field-error" id="error-${item.id}"></div>
        </form>
      </div>
    </div>
  `;

  grid.appendChild(card);
}

// ── Submit Bid ─────────────────────────────────────────────────
async function submitBid(event, itemId) {
  event.preventDefault();

  const amountInput  = document.getElementById(`amount-${itemId}`);
  const contactInput = document.getElementById(`contact-${itemId}`);
  const errorEl      = document.getElementById(`error-${itemId}`);
  const btn          = document.getElementById(`btn-${itemId}`);

  const amount  = parseFloat(amountInput.value);
  const contact = contactInput.value.trim();

  errorEl.textContent = '';
  btn.disabled    = true;
  btn.textContent = 'Placing…';

  try {
    const res  = await fetch(`${BASE}/items/${itemId}/bid`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, contact }),
    });

    const data = await res.json();

    if (!res.ok) {
      const message = extractError(data);
      errorEl.textContent = message;
      showToast(message, 'error');
    } else {
      amountInput.value  = '';
      contactInput.value = '';
      showToast(`Bid of ${formatCurrency(data.current_bid)} placed successfully!`, 'success');
    }
  } catch (err) {
    errorEl.textContent = 'Network error. Please try again.';
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Place Bid';
  }
}

// ── Auction Status & Countdown ─────────────────────────────────
async function checkAuctionStatus() {
  const res  = await fetch(`${BASE}/auction/status`);
  const data = await res.json();

  if (!data.is_open) {
    showAuctionClosed();
    return;
  }

  const endTime = new Date(data.ends_at);
  const interval = setInterval(() => {
    const remaining = endTime - Date.now();
    if (remaining <= 0) {
      clearInterval(interval);
      showAuctionClosed();
    } else {
      updateCountdown(remaining);
    }
  }, 1000);
}

function showAuctionClosed() {
  document.querySelectorAll('.btn-bid').forEach(btn => {
    btn.disabled    = true;
    btn.textContent = 'Auction Closed';
  });
  showToast('The auction has closed. Thank you for participating!', 'info');
}

function updateCountdown(ms) {
  const h  = Math.floor(ms / 3_600_000);
  const m  = Math.floor((ms % 3_600_000) / 60_000);
  const s  = Math.floor((ms % 60_000) / 1_000);
  const el = document.getElementById('countdown');
  if (el) el.textContent = `Closes in ${h}h ${m}m ${s}s`;
}

// ── Toast ──────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3600);
}

// ── Helpers ────────────────────────────────────────────────────

/**
 * FastAPI returns two different error shapes:
 *   - 400 from our own code:  { detail: "plain string" }
 *   - 422 from Pydantic:      { detail: [{ loc, msg, type }, ...] }
 * This normalises both into a single readable string.
 */
function extractError(data) {
  if (!data?.detail) return 'Something went wrong.';
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map(e => e.msg).join('. ');
  }
  return 'Something went wrong.';
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Init ───────────────────────────────────────────────────────
loadItems();
connectWS();
checkAuctionStatus();