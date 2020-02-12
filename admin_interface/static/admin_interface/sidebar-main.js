jQuery(function($) {
  // Dropdown menu
  $(".sidebar-dropdown > a").click(function() {
    $(".sidebar-submenu").slideUp(200);
    if (
      $(this)
        .parent()
        .hasClass("menu-open")
    ) {
      $(".sidebar-dropdown").removeClass("menu-open");
      $(this)
        .parent()
        .removeClass("menu-open");
    } else {
      $(".sidebar-dropdown").removeClass("menu-open");
      $(this)
        .next(".sidebar-submenu")
        .slideDown(200);
      $(this)
        .parent()
        .addClass("menu-open");
    }
  });
});
