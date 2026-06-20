function start_river(data) {
  const layer = document.getElementById('river');
  const n = data.length;
  const dur = 30;

  data.forEach(function (d, i) {
    const el = document.createElement('div');
    el.className = 'drift';
    el.style.top = (4 + Math.random() * 74) + 'vh';
    el.style.animationDuration = dur + 's';
    // negative delay distributes the frames across the crossing immediately,
    // evenly spaced and in chronological order
    el.style.animationDelay = (-(dur / n) * i) + 's';
    el.innerHTML = '<img src="' + d.url + '"><div class="yr">' + (d.year || '') + '</div>';
    layer.appendChild(el);
  });
}
