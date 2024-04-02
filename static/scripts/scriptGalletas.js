function toggleMenu() {
  var menu = document.getElementById("menu");
  var container = document.querySelector(".container");
  
  if (menu.classList.contains("menu-open")) {
      menu.classList.remove("menu-open");
      container.style.paddingLeft = "0";
  } else {
      menu.classList.add("menu-open");
      container.style.paddingLeft = menu.offsetWidth + "px";
  }
}