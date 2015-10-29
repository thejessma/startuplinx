$(function() {
  var moveLeft = 20;
  var moveDown = 10;

  $('img.employeephoto').load(function(){
        var height = $(this).height();
        var width = $(this).width();
        if(width>height){
            $(this).addClass('wide-img');
        }else{
            $(this).addClass('tall-img');
        }
  });

  /*
   TODO failed attempt at hover -- either fix or remove
  $('.employeecontainer').each(function(idx, obj) {
      var employeeDom = jQuery($(this).find('.employee'));

      employeeDom.hover(function(e) {
          var teampopupDom = jQuery($(this).find(".teampopup")[0]);
          teampopupDom.show();
      }, function() {
          var teampopupDom = jQuery($(this).find(".teampopup")[0]);
          teampopupDom.hide();
      });

      employeeDom.mousemove(function (e) {
          var teampopupDom = jQuery($(this).find(".teampopup")[0]);
          teampopupDom.css('top', e.pageY + moveDown).css('left', e.pageX + moveLeft);
      });
  });
  */

});

var main = function() {

  $('.linxedbutton').click(function(){
    $('html,body').animate({
      scrollTop:$(".connect").offset().top}, 1000);
}
  );
}

$(document).ready(main);