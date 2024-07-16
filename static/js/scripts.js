document.querySelector('.navbar-toggler').addEventListener('click', function() {
  document.querySelector('.sidebar').classList.toggle('show');
  document.querySelector('main').classList.toggle('sidebar-open');
});
