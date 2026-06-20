function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function get_after(strip, x) {
  const tiles = [].slice.call(strip.querySelectorAll('.tile:not(.dragging)'));
  let closest = { offset: -Infinity, element: null };
  tiles.forEach(function (child) {
    const box = child.getBoundingClientRect();
    const offset = x - box.left - box.width / 2;
    if (offset < 0 && offset > closest.offset) closest = { offset: offset, element: child };
  });
  return closest.element;
}

function start_sort(data) {
  const strip = document.getElementById('strip');
  let dragEl = null;

  shuffle(data.slice()).forEach(function (d) {
    const el = document.createElement('div');
    el.className = 'tile';
    el.draggable = true;
    el.dataset.frame = d.frame;
    el.innerHTML = '<img src="' + d.url + '">';

    el.addEventListener('dragstart', function () { dragEl = el; el.classList.add('dragging'); });
    el.addEventListener('dragend', function () { el.classList.remove('dragging'); });

    strip.appendChild(el);
  });

  strip.addEventListener('dragover', function (e) {
    e.preventDefault();
    if (!dragEl) return;
    const after = get_after(strip, e.clientX);
    if (after == null) strip.appendChild(dragEl);
    else strip.insertBefore(dragEl, after);
  });
}

function check_sort() {
  const tiles = [].slice.call(document.querySelectorAll('.tile'));
  const frames = tiles.map(function (t) { return +t.dataset.frame; });
  const sorted = frames.slice().sort(function (a, b) { return a - b; });

  let ok = true;
  tiles.forEach(function (t, i) {
    if (frames[i] === sorted[i]) {
      t.classList.add('right'); t.classList.remove('wrong');
    } else {
      t.classList.add('wrong'); t.classList.remove('right'); ok = false;
    }
  });

  document.getElementById('status').textContent =
    ok ? "perfect — that's the original order" : 'not quite — keep dragging';
}
