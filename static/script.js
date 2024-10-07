
$('#prevbut').bind('click', function(e) {
    $('#myCarousel').carousel('prev');
  });
  $('#nextbut').bind('click', function(e) {
    $('#myCarousel').carousel('next');
  });
  //search bar                                     
  let slideIndex = 0;
  showSlides();
  
  function showSlides() {
    let i;     
    let slides = document.getElementsByClassName("mySlides");
    for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1 }
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 2000); // Change image every 2 seconds
  }
  //searching
  const club_titles = [];
  //const club_images = ["static/images/Robotics_Club.jpg", "static/images/ski.jpg", "static/images/turkish.jpg", "static/images/untitled.jpg"];
  
  function on_search() {
  
  }
  
  function edge() {
    for (let i = 0; i < 200; i++) {
      club_titles.push(document.getElementById("club" + i).outerHTML);
  
    }
  
  
  }
