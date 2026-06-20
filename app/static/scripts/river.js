var RIVER_POOL = [];

function even_sample(arr, k) {
  if (k >= arr.length) return arr.slice();
  var step = arr.length / k;
  var out = [];
  for (var i = 0; i < k; i++) out.push(arr[Math.floor(i * step)]);
  return out;
}

function render_river() {
  var layer = document.getElementById('river');
  var count = +document.getElementById('opt-count').value;
  var size = +document.getElementById('opt-size').value;
  var speed = +document.getElementById('opt-speed').value;
  var dur = Math.round(640 / speed) / 10;  // higher speed = shorter crossing

  document.getElementById('out-count').textContent = count;
  document.getElementById('out-size').textContent = size + 'px';
  document.getElementById('out-speed').textContent = speed;

  // even sample keeps the full chronological range while changing density
  var frames = even_sample(RIVER_POOL, count);
  var n = frames.length;

  layer.innerHTML = '';
  frames.forEach(function (d, i) {
    var el = document.createElement('div');
    el.className = 'drift';
    el.style.top = (3 + Math.random() * 76) + 'vh';
    el.style.animationDuration = dur + 's';
    // negative delay spreads the frames across the crossing immediately, in order
    el.style.animationDelay = (-(dur / n) * i) + 's';
    el.innerHTML = '<img src="' + d.url + '" style="width:' + size + 'px">' +
      '<div class="yr">' + (d.year || '') + '</div>';
    layer.appendChild(el);
  });
}

function start_river(data) {
  RIVER_POOL = data;
  ['opt-count', 'opt-size', 'opt-speed'].forEach(function (id) {
    document.getElementById(id).addEventListener('input', render_river);
  });
  render_river();
}
