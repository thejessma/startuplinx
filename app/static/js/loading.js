var main = function() {

  $('.bufferbody').waypoint(function() {
    $('.bufferlinx').addClass('animated fadeInLeft').css( 'display', 'inline-block' );
    $('.quote').addClass('animated fadeInDown').css( 'display', 'inline-block' );
     setTimeout(function(){
      $('.quote').css('display','none');
      $('.quote2').addClass('animated fadeInDown').css( 'display', 'block' )},4000);
     setTimeout(function(){
      $('.quote2').css('display','none');
      $('.quote3').addClass('animated fadeInDown').css( 'display', 'inline-block' )},8000);
     setTimeout(function(){
      $('.quote3').css('display','none');
      $('.quote4').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 12000);
     setTimeout(function(){
      $('.quote4').css('display','none');
     $('.quote5').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 16000);
     setTimeout(function(){
      $('.quote5').css('display','none');
     $('.quote6').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 20000);
     setTimeout(function(){
      $('.quote6').css('display','none');
     $('.quote7').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 24000);
     setTimeout(function(){
      $('.quote7').css('display','none');
     $('.quote8').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 28000);
     setTimeout(function(){
      $('.quote8').css('display','none');
     $('.quote9').addClass('animated fadeInDown').css( 'display', 'inline-block' )}, 32000);
    
     $('.moment').addClass('animated fadeInLeft').css( 'display', 'block' );
    $('.runninglinx').addClass('animated fadeInRight').css( 'display', 'inline-block' );
   $('.bodyline').addClass('animated fadeInRight').css( 'display', 'inline-block' );}
  , {offset:'100px'}
  );
};


$(document).ready(main);