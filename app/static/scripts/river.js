var RIVER_POOL = [];
var RIVER_TIMER = null;
var RIVER_IDX = 0;
var RIVER_BAND = { min: 0, max: 0 };

function update_band(size) {
  // keep every frame fully inside the river band so none slides under the
  // footer; account for image height (~4:3) + the year label
  var h = document.getElementById('river').clientHeight || Math.round(window.innerHeight * 0.6) || 500;
  var frame_h = size * 0.75 + 18;
  RIVER_BAND.min = 8;
  RIVER_BAND.max = Math.max(RIVER_BAND.min + 40, h - frame_h - 8);
}

function spawn_drift(frame, dur, neg_delay) {
  var el = document.createElement('div');
  el.className = 'drift';
  el.style.top = (RIVER_BAND.min + Math.random() * (RIVER_BAND.max - RIVER_BAND.min)) + 'px';
  el.style.animationDuration = dur + 's';
  if (neg_delay) el.style.animationDelay = (-neg_delay) + 's';
  el.innerHTML = '<img src="' + frame.url + '">' +
    '<div class="yr">' + (frame.year || '') + '</div>';
  el.addEventListener('animationend', function () { el.remove(); });
  document.getElementById('river').appendChild(el);
}

function render_river() {
  var count = +document.getElementById('opt-count').value;
  var size = +document.getElementById('opt-size').value;
  var speed = +document.getElementById('opt-speed').value;
  var dur = Math.round(640 / speed) / 10;  // higher speed = shorter crossing

  document.getElementById('out-count').textContent = count;
  document.getElementById('out-size').textContent = size + 'px';
  document.getElementById('out-speed').textContent = speed;

  var layer = document.getElementById('river');
  layer.style.setProperty('--river-size', size + 'px');
  update_band(size);
  if (RIVER_TIMER) clearInterval(RIVER_TIMER);
  layer.innerHTML = '';
  if (!RIVER_POOL.length) return;

  var n = RIVER_POOL.length;
  // initial fill: spread `count` frames across the screen in chronological
  // order — oldest furthest left (most progressed), newest just entering
  for (var j = 0; j < count; j++) {
    spawn_drift(RIVER_POOL[j % n], dur, dur * ((count - 1 - j) / count));
  }
  RIVER_IDX = count;

  // then keep feeding the next frame in order from the right edge, so the
  // river flows through the whole pool oldest->newest before it wraps
  RIVER_TIMER = setInterval(function () {
    // when the tab is hidden, CSS animations pause but setInterval keeps
    // firing — skip so frames don't pile up at the entry edge
    if (document.hidden || layer.childElementCount >= count + 4) return;
    spawn_drift(RIVER_POOL[RIVER_IDX % n], dur, 0);
    RIVER_IDX++;
  }, (dur / count) * 1000);
}

function start_river(data) {
  RIVER_POOL = data;
  ['opt-count', 'opt-size', 'opt-speed'].forEach(function (id) {
    document.getElementById(id).addEventListener('input', render_river);
  });
  render_river();
}
