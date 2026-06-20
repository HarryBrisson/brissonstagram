function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function start_match(data) {
  const board = document.getElementById('board');
  const deck = shuffle(data.concat(data.map(d => Object.assign({}, d))));

  let first = null, lock = false, matched = 0, moves = 0;

  deck.forEach(function (card) {
    const el = document.createElement('div');
    el.className = 'card';
    el.innerHTML =
      '<div class="card-back"></div>' +
      '<div class="card-front"><img src="' + card.url + '"></div>';

    el.addEventListener('click', function () {
      if (lock || el.classList.contains('flipped') || el.classList.contains('done')) return;
      el.classList.add('flipped');

      if (!first) { first = { el: el, id: card.id }; return; }

      moves++;
      document.getElementById('moves').textContent = moves;

      if (first.id === card.id) {
        first.el.classList.add('done');
        el.classList.add('done');
        matched++;
        first = null;
        if (matched === data.length) {
          document.getElementById('status').textContent = 'you found them all in ' + moves + ' moves';
        }
      } else {
        lock = true;
        const prev = first;
        first = null;
        setTimeout(function () {
          prev.el.classList.remove('flipped');
          el.classList.remove('flipped');
          lock = false;
        }, 800);
      }
    });

    board.appendChild(el);
  });
}
