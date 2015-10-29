var main = function() {

  // Lazy loading sucks
  // 
  //  $("img.friends").unveil(200);
  //  $("img.startup").unveil(200);
  /*  jQuery("img.friends").lazy({
        threshold: 1000,
        enableThrottle: true,
        throttle: 250
    });
    jQuery("img.startup").lazy({
        threshold: 1000,
        enableThrottle: true,
        throttle: 250
    });*/

	/*$('div.feedRecommendations').waypoint(function(direction) {

        if (direction==='down') {

            $('div.recHelp').removeClass('animated fadeOut');

            $('div.recHelp').addClass('animated fadeInUp').css( 'display', 'block' );

        }
        else if (direction==='up') {

            $('div.recHelp').removeClass('animated fadeInUp');

            $('div.recHelp').addClass('animated fadeOut');

        }
	}, {offset:'300'});*/

    $('.limited_start').click(function(){
        $('.limited_img').css('display','none');
        $('.limited_close').css('display','none');
        $('.limited_text').css('display','none');
        $('.limited_start').css('display','none');
        $('.limited_offer').addClass('limited_hidden').css('width','auto');
        
    });

    $('.limited_close').click(function(){
        $('.limited_img').css('display','none');
        $('.limited_close').css('display','none');
        $('.limited_text').css('display','none');
        $('.limited_start').css('display','none');
        $('.limited_offer').addClass('limited_hidden').css('width','auto');
        
    });

    $('.limited_title').click(function(){
        console.log('hi');
        $('.limited_img').css('display','inline-block');
        $('.limited_close').css('display','block');
        $('.limited_text').css('display','inline-block');
        $('.limited_start').css('display','inline-block');
        $('.limited_offer').removeClass('limited_hidden').css('width','50vw');
        
    });

    var filtershow;
    filtershow = 0;

    $('div.feed').waypoint(function(direction) {

        if (direction==='down') {


            $('div.feedfilter').removeClass('animated fadeOutUp');

            $('div.feedfilter').addClass('animated fadeInDown').css( 'display', 'block' );

            setTimeout(function(){$('.filterhide').addClass('animated fadeInDown').css('display','inline-block')}, 500);
        
           $('.filterhidetop').addClass('animated fadeOut').css('display','none');

            $('.filterhide').removeClass('animated fadeOut');

            filtershow=1;
        }
        else if (direction==='up') {

            $('div.feedfilter').removeClass('animated fadeInDown');

            $('div.feedfilter').addClass('animated fadeOutUp');

             setTimeout(function(){$('.filterhidetop').addClass('animated fadeIn').css('display','inline-block')}, 500);

           $('.filterhide').addClass('animated fadeOut').css('display','none');

            $('.filterhidetop').removeClass('animated fadeOut');

            filtershow=0;
        }

    }, {offset:'100'});

    $('.filterhide').click(function(){

        if (filtershow===1) {
        
            $('div.feedfilter').removeClass('animated fadeInDown');

            $('div.feedfilter').addClass('animated fadeOutUp');

            setTimeout(function(){$('.filterhidetop').addClass('animated fadeIn').css('display','inline-block')}, 500);

            $('.filterhide').addClass('animated fadeOut').css('display','none');

            $('.filterhidetop').removeClass('animated fadeOut');

            filtershow=0;
        }

        else if (filtershow===0) {
        
            $('div.feedfilter').removeClass('animated fadeOutUp');

            $('div.feedfilter').addClass('animated fadeInDown').css( 'display', 'block' );

            setTimeout(function(){$('.filterhide').addClass('animated fadeInDown').css('display','inline-block')}, 500);
        
            $('.filterhidetop').addClass('animated fadeOut').css('display','none');

            $('.filterhide').removeClass('animated fadeOut');

            filtershow=1;
        }

    });

    $('.filterhidetop').click(function(){

        if (filtershow===1) {
        
            $('div.feedfilter').removeClass('animated fadeInDown');

            $('div.feedfilter').addClass('animated fadeOutUp');

            setTimeout(function(){$('.filterhidetop').addClass('animated fadeIn').css('display','inline-block')}, 500);

            $('.filterhide').addClass('animated fadeOut').css('display','none');

            $('.filterhidetop').removeClass('animated fadeOut');

            filtershow=0;
        }

        else if (filtershow===0) {

            $('div.feedfilter').removeClass('animated fadeOutUp');

            $('div.feedfilter').addClass('animated fadeInDown').css( 'display', 'block' );

            setTimeout(function(){$('.filterhide').addClass('animated fadeInDown').css('display','inline-block')}, 500);
        
            $('.filterhidetop').addClass('animated fadeOut').css('display','none');

            $('.filterhide').removeClass('animated fadeOut');

            filtershow=1;
        }

    });

    $('.forwardarrow').click(function(){
        var currentSlide = $('.active-slide');
        var nextSlide=currentSlide.next();
        var prevSlide=currentSlide.prev();

        if(nextSlide.next().length == 0) {
            $('.forwardarrow').css('display','none')
        }

        if(prevSlide.prev().length = 1) {
            $('.backarrow').css('display','inline-block')
        };

        currentDot = $('.active-dot');
        nextDot = currentDot.next();
        nextDot.addClass('active-dot');
        currentDot.removeClass('active-dot');
        

        currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');;
        nextSlide.fadeIn(600).addClass('active-slide').css('display','inline-block');
   
   		});

   	$('.backarrow').click(function(){
        var currentSlide=$('.active-slide');
        var prevSlide=currentSlide.prev();
        var nextSlide=currentSlide.next();
        
        if (prevSlide.prev().length==0) {
            $('.backarrow').css('display','none');
        };

        if(nextSlide.next().length = 1) {
            $('.forwardarrow').css('display','inline-block')
        };
        
        var currentDot = $('.active-dot');
        var prevDot = currentDot.prev();
        
        
        prevDot.addClass('active-dot');
        currentDot.removeClass('active-dot');
        
        currentSlide.fadeOut(600).removeClass('active-slide').css('display','none');
        prevSlide.fadeIn(600).addClass('active-slide').css('display','inline-block');
        

    	});
   	$('.learnmore').click(function(){
   		$('.statsinfo').addClass('animated fadeInDown').css('display','block');
   	})

   	$('.startupintro').click(function(){
   		$('.linxedscreen').css('display','none');
   		$('.profilescreen').addClass('animated fadeIn').css('display','block');
   	})

   	$('.connectbuttoninline').click(function(){
   		$('.profilescreen').css('display','none');
   		$('.linxedscreen').addClass('animated fadeIn').css('display','block');
   	})

    $("#filter_team_size").ionRangeSlider({
        transform: logSliderTransform,
        hide_min_max: true,
        keyboard: true,
        min: 500,
        max: 4000,
        from: 500,
        to: 4000,
        type: 'double',
        step: 1,
        onChange: teamSizeFilterChangeCallback
    });

    $("#filter_funding").ionRangeSlider({
        transform: logSliderTransform,
        hide_min_max: true,
        keyboard: true,
        min: 3000,
        max: 9500,
        from: 3000,
        to: 9500,
        type: 'double',
        step: 1,
        prefix: "$",
        onChange: fundingFilterChangeCallback
    });

    $("#filter_founded_year").ionRangeSlider({
        transform: yearSliderTransform,
        hide_min_max: true,
        keyboard: true,
        min: 2000,
        max: 2014,
        from: 2000,
        to: 2014,
        type: 'double',
        step: 0.1,
        prettify_enabled: false,
        onChange: foundedYearFilterChangeCallback 
    });

    $("#filter_series").ionRangeSlider({
        transform: seriesSliderTransform,
        hide_min_max: true,
        keyboard: true,
        min: 0,
        max: 7,
        from: 0,
        to: 7,
        type: 'double',
        step: 0.1,
        onChange: seriesFilterChangeCallback
    });

    $('#filter_location').Watermark('E.g. New York, California, France');
    $('#filter_location').on('keyup', locationFilterChange);

    $('#filter_unfavorite').click(unfavoriteFilterClick);
    $('#filter_favorite').click(favoriteFilterClick);
};

// Slider Transforms for visualization

function compact_moneyz(moneyz) {
    if (moneyz >= 1000000000) {
        return Math.round(moneyz/1000000000).toString() + 'B'
    }
    if (moneyz >= 1000000) {
        return Math.round(moneyz/1000000).toString() + 'M'
    }
    if (moneyz >= 1000) {
        return Math.round(moneyz/1000).toString() + 'K'
    }
    return moneyz;
}

function truncateMinMaxTransform(value, min, max) {
    var result = value;
    if (result <= min) {
        result = 0;
    } else if (result >= max) {
        result = Infinity;
    }
    return result;
}

function seriesSliderTransform(value, min, max, numeric) {
    if (typeof(numeric) === 'undefined') {
        numeric = false;
    }
    value = Math.round(value);
    if (value <= min) {
        if (numeric) {
            return 0;
        } else {
            return 'Seed';
        }
    }
    if (value >= max) {
        if (numeric) {
            return Infinity;
        } else {
            return 'Z';
        }
    }
    var result = value;
    if (!numeric) {
        result = String.fromCharCode(65 + result - 1);
    }
    return result;
}

function yearSliderTransform(value, min, max, numeric) {
    if (typeof(numeric) === 'undefined') {
        numeric = false;
    }
    if (value <= min) {
        if (numeric) {
            return -Infinity;
        } else {
            return '-&infin;';
        }
    }
    return Math.round(value);
}

function logSliderTransform(value, min, max, numeric) {
    if (typeof(numeric) === 'undefined') {
        numeric = false;
    }
    var result = value;
    if (value <= min) {
        result = 0;
    } else if (value >= max) {
        if (numeric) {
            result = Infinity;
        } else {
            result = '&infin;';
        }
    } else {
        result = Math.round(Math.pow(10, value / 1000));
        if (!numeric) {
            result = compact_moneyz(result);
        }
    }
    return result;
}

// Manage visibility of companies based on filters

var FILTERS_COUNT = 6;

function applyFilter(dom, filter_name, does_match) {
    // update filter value
    did_match = dom.data(filter_name);
    if (typeof did_match === 'undefined') {
        did_match = true; // by default, all filters are matched 
    }
    dom.data(filter_name, does_match);
    // reflect change in total # of filters that match
    matched_filters_count = dom.data('matched_filters');
    if (typeof matched_filters_count === 'undefined') {
        matched_filters_count = FILTERS_COUNT; // by default, all filters are matched
    }
    if (!did_match && does_match) {
        matched_filters_count++;
    } else if (did_match && !does_match) {
        matched_filters_count--;
    }
    dom.data('matched_filters', matched_filters_count);
    // toggle visibility based on # of matched filters
    if (matched_filters_count == FILTERS_COUNT) {
        dom.show();
    } else {
        dom.hide();
    }
}

// Slider callbacks for reflecting the filter changes

function foundedYearFilterChangeCallback(result) {
    from = yearSliderTransform(result.from, result.min, result.max, /*numeric */ true);
    to = yearSliderTransform(result.to, result.min, result.max, /*numeric */ true);
    $(".startupwrapper").each(function(idx, obj) {
        var yearFoundedDom = jQuery(jQuery($(this)).find(".yearfoundedvalue")[0]);
        var year_founded = parseInt(yearFoundedDom.val());
        var does_match = (year_founded >= from && year_founded <= to);
        applyFilter($(this), 'year_founded', does_match);
    });
}

function teamSizeFilterChangeCallback(result) {
    from = logSliderTransform(result.from, result.min, result.max, /*numeric */ true);
    to = logSliderTransform(result.to, result.min, result.max, /*numeric */ true);
    $(".startupwrapper").each(function(idx, obj) {
        var employeesMinDom = jQuery(jQuery($(this)).find(".employees_min")[0]);
        var employees_min = parseInt(employeesMinDom.val());
        var employeesMaxDom = jQuery(jQuery($(this)).find(".employees_max")[0]);
        var employees_max = parseInt(employeesMaxDom.val());
        min = Math.min(from, employees_min);
        max = Math.max(to, employees_max);
        var does_match = (employees_min <= to && employees_max >= from); 
        applyFilter($(this), 'team_size', does_match);
    });
}

function fundingFilterChangeCallback(result) {
    from = logSliderTransform(result.from, result.min, result.max, /*numeric */ true);
    to = logSliderTransform(result.to, result.min, result.max, /*numeric */ true);
    $(".startupwrapper").each(function(idx, obj) {
        var totalFundingDom = jQuery(jQuery($(this)).find(".totalfundingvalue")[0]); 
        var totalFunding = parseInt(totalFundingDom.val());
        var does_match = (totalFunding >= from && totalFunding <= to);
        applyFilter($(this), 'funding', does_match);
    });
}

function seriesFilterChangeCallback(result) {
    from = seriesSliderTransform(result.from, result.min, result.max, /*numeric */ true);
    to = seriesSliderTransform(result.to, result.min, result.max, /*numeric */ true);
    $(".startupwrapper").each(function(idx, obj) {
        var seriesDom = jQuery(jQuery($(this)).find(".latest_series_value")[0]); 
        var series = parseInt(seriesDom.val());
        var does_match = (series >= from && series <= to); 
        applyFilter($(this), 'series', does_match);
    });
}

function locationFilterChange() {
    query = this.value;
    if (!query) {
        query = "";
    } else {
        query = query.trim().toLowerCase();
    }
    $(".startupwrapper").each(function(idx, obj) {
        var hqDom = jQuery(jQuery($(this)).find(".headquarters_json")[0]); 
        var hq = hqDom.val();
        var res = hq.indexOf(query);
        var does_match = (res > -1); 
        applyFilter($(this), 'location', does_match);
    });
}

function favoritedFilterChange(favs_only) {
    $(".startupwrapper").each(function(idx, obj) {
        var favDom = jQuery(jQuery($(this)).find(".is_favorited")[0]); 
        var is_fav = parseInt(favDom.val());
        var does_match = (is_fav || !favs_only);
        applyFilter($(this), 'favorite', does_match);
    });
}

function unfavoriteFilterClick() {
    $("#filter_favorite").show();
    $("#filter_unfavorite").hide();
    favoritedFilterChange(false);
}

function favoriteFilterClick() {
    $("#filter_favorite").hide();
    $("#filter_unfavorite").show();
    favoritedFilterChange(true);
}

$(document).ready(main);
