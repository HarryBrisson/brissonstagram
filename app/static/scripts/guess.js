function guess(year) {
  const buttons = [].slice.call(document.querySelectorAll('.year-opt'));
  buttons.forEach(function (b) {
    b.disabled = true;
    const y = +b.dataset.year;
    if (y === ANSWER) b.classList.add('right');
    else if (y === year) b.classList.add('wrong');
  });
  document.getElementById('status').textContent =
    (year === ANSWER) ? 'correct — ' + ANSWER : 'nope, it was ' + ANSWER;
}
