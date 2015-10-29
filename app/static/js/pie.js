var main = function() {


	$('.functionbutton').click(function(){
    $('html,body').animate({
      scrollTop:$(".solution1").offset().top}, 400);
}
  );

$('.button1').click(function(){
	$('.original').removeClass('animated fadeInRight active-text').css('display','none');
	 $('.discovertext').addClass('animated fadeInRight active-text').css('display', 'inline-block');
     $('.connecttext').removeClass('animated fadeInRight active-text').css('display', 'none');
     var currentSlide= $('.active-slide');
     var currentDot = $('.active-dot');

     var discoverSlide= $('.2');
     var discoverDot = $('.D2');

    currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');
    currentDot.removeClass('active-dot');

     discoverSlide.fadeIn(600).addClass('active-slide').css('display', 'inline-block');;
     discoverDot.addClass('active-dot');


 }
 );

$('.button2').click(function(){
	$('.original').removeClass('animated fadeInRight active-text').css('display','none');
	 $('.connecttext').addClass('animated fadeInRight active-text').css('display', 'inline-block');
     $('.discovertext').removeClass('animated fadeInRight active-text').css('display', 'none');

        var currentSlide= $('.active-slide');
     var currentDot = $('.active-dot');

     var discoverSlide= $('.3');
     var discoverDot = $('.D3');

    currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');
    currentDot.removeClass('active-dot');

     discoverSlide.fadeIn(600).addClass('active-slide').css('display', 'inline-block');;
     discoverDot.addClass('active-dot');

 }
 );

$('.forwardarrowhome').click(function(){
        var currentSlide = $('.active-slide');
        var nextSlide=currentSlide.next();
 
         if(nextSlide.length == 0) {
            nextSlide= $('.screenimgwrapper').first();
          }

        currentDot = $('.active-dot');
        nextDot = currentDot.next();

        if (nextDot.length == 0){
          nextDot=$('.dot').first();
        }

        var currentText= $('.active-text');
        var nextText=currentText.next();

        if (nextText.length ==0){
        	nextText=$('.original');
        }

        nextText.addClass('active-text');
        currentText.removeClass('active-text');
        nextDot.addClass('active-dot');
        currentDot.removeClass('active-dot');

        currentText.removeClass('animated fadeInRight').css('display','none');
        nextText.addClass('animated fadeInRight').css('display','inline-block');
        
        currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');;
        nextSlide.fadeIn(600).addClass('active-slide').css('display','inline-block');
   
      });


$('.backarrowhome').click(function(){
        var currentSlide=$('.active-slide');
        var prevSlide=currentSlide.prev();
       
        if(prevSlide.length == 0) {
          prevSlide = $('.screenimgwrapper').last();
        }
        
        var currentDot = $('.active-dot');
        var prevDot = currentDot.prev();

        if(prevDot.length == 0) {
          prevDot = $('.dot').last();
        }
        
         var currentText= $('.active-text');
        var prevText=currentText.prev();

        if (prevText.prev().length ==0){
        	prevText=$('.connecttext');
        }

        prevText.addClass('active-text');
        currentText.removeClass('active-text');
        prevDot.addClass('active-dot');
        currentDot.removeClass('active-dot');

        currentText.removeClass('animated fadeInRight').css('display','none');
        prevText.addClass('animated fadeInRight').css('display','inline-block');

        currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');
        prevSlide.fadeIn(600).addClass('active-slide').css('display','inline-block');
        

      });

$('.slide-1').waypoint(function(){
	$('.logo-top').addClass('animated fadeIn');
	$('.meetjob').addClass('animated fadeInDown').css('display','block');
	$('.joinmini').addClass('animated fadeInRight').css('display','inline-block');

})
 

  $('.basicinfo').waypoint(function(){
    $('.titlefiller').css('display','none');
    $('.titlemission').addClass('animated fadeInDown').css('display','inline-block');
  })

   	$('.mission').waypoint(function() {
   	$('.titlefiller').css('display','none');
   	$('.missiontextfiller').css('display','none');
    $('.movingicons').addClass('animated fadeInLeft').css('display','inline-block');
   	 $('.missiontext').addClass('animated fadeInRight').css( 'display', 'inline-block' );}
	, {offset:'300px'}
	);

	$('.problem').waypoint(function() {
   	$('.titleproblem').addClass('animated fadeInDown').css( 'display', 'block' );
 	 $('.problemtext').addClass('animated fadeInDown').css( 'display', 'inline-block' );}
	, {offset:'500px'}
	);

	$('.solution').waypoint(function() {
   	$('.titlesolutionfiller').css('display','none');
 	 $('.titlesolution').addClass('animated fadeInDown').css( 'display', 'block' );
 	   $('.subtitle').addClass('animated fadeInDown').css( 'display', 'block' );}
	, {offset:'500px'}
	);

	$('.solution').waypoint(function() {
   	$('.titlesolutionfiller').css('display','none');
   	//$('.solutioncol1filler').css('display','none');
 	 setTimeout(function(){$('.solutioncol1').addClass('animated fadeInDown').css( 'display', 'inline-block' )},0);
 	 //$('.solutioncol2filler').css('display','none');
 	setTimeout(function(){$('.solutioncol2').addClass('animated fadeInDown').css( 'display', 'inline-block' )},0);
 	 //$('.solutioncol3filler').css('display','none');
 	 setTimeout(function(){$('.solutioncol3').addClass('animated fadeInDown').css( 'display', 'inline-block' )},0);
	}, {offset:'400px'}
	);

  $('.solutionimg1').hover(function() {
    $('.solutionimg1').addClass('animated pulse');
  });
  $('.solutionimg2').hover(function() {
    $('.solutionimg2').addClass('animated pulse');
  });
  $('.solutionimg3').hover(function() {
    $('.solutionimg3').addClass('animated pulse');
  });

	$('.functionsbox').waypoint(function() {
   	$('.titlediscoverfiller').css('display','none');
   	$('.discovericon').addClass('animated fadeInDown').css( 'display', 'inline-block' );
   	 $('.discoverp').addClass('animated fadeInRight').css( 'display', 'block' );
 	  $('.discoverimg').addClass('animated fadeInLeft').css( 'display', 'inline-block' );
 	 $('.titlediscover').addClass('animated fadeInDown').css( 'display', 'block' );
 }
	, {offset:'500px'}
	);




	//-----------NAVIGATION------------------//

	$('.content-sections').waypoint(function(direction) {

 	if (direction==='down') {
 		$('.header').removeClass('animated fadeOut');
 		$('.header').addClass('animated fadeInDown').css('display','inline-block');

 	
}
	else if (direction==='up') {
	$('div.header').removeClass('animated fadeInDown');
	$('div.header').addClass('animated fadeOut');
 	
}
	});

  $('.bufferbody').waypoint(function() {
    $('.bufferlinx').addClass('animated fadeInLeft').css( 'display', 'inline-block' );
    $('.quote').addClass('animated fadeInDown').css( 'display', 'inline-block' );
     setTimeout(function(){
      $('.quote').css('display','none');
      $('.quote2').addClass('animated fadeInDown').css( 'display', 'inline-block' )},4000);
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


var controller = new ScrollMagic({
    globalSceneOptions: {
        triggerHook: "onLeave"
    }
});

var pinani = new TimelineMax()
    
    .add([
    	TweenMax.from("#wipe", 180, {y:1307, autoKill: false}),
    	TweenMax.to("#dis_text", 150, {top: "-60%", autoKill: false}),
    	TweenMax.to("#screen", 150, {y:-1307, autoKill: false}),
      TweenMax.to("#connect_screen", 100, {y:0, autoKill: false})
    ])

    new ScrollScene({
        triggerElement: "#pin",
        duration: 3000,
        autoKill:false
    })
    .setTween(pinani)
    .setPin("#pin")
    .addTo(controller);

 }

  

var $window, root, scrollTop,
	loadedAssetsCounter = 0,
	wiperSF = 20,
	tabletWidth = 1024,
	tabletSmallWidth = 800,
	smallScreenWidth = 600;

var Core = {
	
	init: function() {
		
		$window = $(window);		
		root = $('html, body');
		$window.on('ready scroll', function() {
			scrollTop = $window.scrollTop();
		});
	}
};

var IntroSection = {
	
	el: $('.section-intro'),
	
	wiper: {
	
		el: $('#wiper'),
		sectorEl: $('#wiper path'),
		lastStopEl: $('#wiper stop:last'),
		
		draw: function(start, teta) {
	
			var start_deg = start,
				teta_deg = parseFloat(teta, 10),
				radius = 50,
				large_arc_flag = 0,
				sweep_flag = 0,
				digits = 2,
				start_rad, teta_rad, x, y, pointA, pointB, arc;
		
			if (teta_deg >= 360) { teta_deg = 359.99; }
			if (teta_deg <= -360) { teta_deg = -359.99; }
	
			start_rad = start_deg * Math.PI/180;
			teta_rad = teta_deg * Math.PI/180;
			
			x = Math.cos(start_rad) * radius;
			y = Math.sin(start_rad) * radius;
			pointA = [x+50, 50-y];
			x = Math.cos(start_rad+teta_rad) * radius;
			y = Math.sin(start_rad+teta_rad) * radius;
			pointB = [x+50, 50-y];
		
			if (teta_deg > 180) { large_arc_flag = 1; }
			if (teta_deg < 0) { large_arc_flag = 0; sweep_flag = 1; }
			if (teta_deg < -180) { large_arc_flag = 1; sweep_flag = 1; }
			arc = 'M 50 50 '
				+'L '+pointA[0].toFixed(digits)+' '+pointA[1].toFixed(digits)+' '
				+'A 50 50 '+start_rad.toFixed(digits)+' '
				+ large_arc_flag+' '+sweep_flag+' '
				+ pointB[0].toFixed(digits)+' '+pointB[1].toFixed(digits)+' '
				+'Z';
		
			this.sectorEl.attr('d', arc);
		},
	},


	init: function() {
			
		IntroSection.wiper.draw(0, 240);

		$window.on('ready scroll', function() {
				

					var scrollFactor = scrollTop / wiperSF;
					if (scrollFactor <= 120) {
						IntroSection.wiper.draw(0, Math.min(240 + scrollFactor, 360));
						if (IntroSection.el.hasClass('reversed')) {
							IntroSection.el.removeClass('reversed');
						}
					} else if (scrollFactor > 120 && scrollFactor < 999) {
						if (!IntroSection.el.hasClass('reversed')) {
							IntroSection.el.addClass('reversed');
						}
						var t = Math.max(360 - (scrollFactor - 120), 180);
						IntroSection.wiper.draw(0, t);
					}

					
				});

			var controller = new ScrollMagic();
			var scrollFactor = wiperSF;
			
			var scene1 = new ScrollScene({ offset: scrollFactor * 10, duration: scrollFactor*30})
				.setTween(TweenMax.to('#slide1-2', 0.5, {alpha:0}))
				.addTo(controller);

			var scene1 = new ScrollScene({ offset: scrollFactor * 10, duration: scrollFactor*30})
				.setTween(TweenMax.to('#slide1-1', 0.5, {alpha:0}))
				.addTo(controller);

			var scene2 = new ScrollScene({ offset: scrollFactor * 50, duration: scrollFactor*60})
				.setTween(TweenMax.to('#slide2', 0.5, {alpha:1, visibility:'visible',y:"0"}))
				.addTo(controller);

			var scene3 = new ScrollScene({ offset: scrollFactor * 140, duration: scrollFactor*60})
				.setTween(TweenMax.to('#slide2', 0.5, {alpha:0}))
				.addTo(controller);

			var scene4 = new ScrollScene({ offset: scrollFactor * 205, duration: scrollFactor*150})
				.setTween(TweenMax.to('#slide3', 0.5, {alpha:1, visibility: 'visible', y:"0"}))
				.addTo(controller);

			var scene3 = new ScrollScene({ offset: scrollFactor * 300, duration: scrollFactor*60})
				.setTween(TweenMax.to('#slide3', 0.5, {alpha:0}))
				.addTo(controller);


		}};


  $( "#bkgd" ).animate({
    top:"-20000"
  }, 200000, function() {
    // Animation complete.
  });


$(document).ready(main);

$(function() {
	
		Core.init();
		IntroSection.init();

});
