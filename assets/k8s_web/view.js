CTFd._internal.challenge.data = undefined;

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function() {};

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function() {};

CTFd._internal.challenge.submit = function(preview) {
  var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());
  var submission = CTFd.lib.$("#challenge-input").val();

  var body = {
    challenge_id: challenge_id,
    submission: submission
  };
  var params = {};
  if (preview) {
    params["preview"] = true;
  }

  return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
    if (response.status === 429) {
      // User was ratelimited but process response
      return response;
    }
    if (response.status === 403) {
      // User is not logged in or CTF is paused.
      return response;
    }
    return response;
  });
};

function get_k8s_status(id) {
  $.get("/api/v1/k8s/get?challenge_id="+id, function(result) {
    if (result.InstanceRunning) {
        if (result.ThisChallengeInstance) {
          connectionPort = result.ConnectionPort
          connectionURL = result.ConnectionURL + ':' + String(connectionPort)
          expireTime = result.ExpireTime

          $('#k8s_connection_link').attr('href', connectionURL)
          $('#k8s_connection').css('display', 'block')
          var countDownDate = new Date(parseInt(result.ExpireTime) * 1000);
          var countDownIntervalID = setInterval(function() {
              var now = new Date().getTime();
              var distance = countDownDate - now;
              var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
              var seconds = Math.floor((distance % (1000 * 60)) / 1000);
              if (seconds < 10) {
                  seconds = "0" + seconds
              }
              $('#k8s_countdown').html('Instance expires in ' + minutes + ':' + seconds);
              if (distance < 0) {
                  clearInterval(countDownIntervalID);
                  $('#k8s_start').css('display', 'block')
                  $('#k8s_stop').css('display', 'none')
                  $('#k8s_connection').css('display', 'none')
                  $('#k8s_countdown').css('display', 'none')
                  $('#k8s_extend').css('display', 'none')
              }
          }, 1000);
          $('#k8s_countdown').css('display', 'block')
          $('#k8s_start').css('display', 'none')
          $('#k8s_stop').css('display', 'inline-block')
          if (result.ExtendAvailable) {
            $('#k8s_extend').css('display', 'inline-block')
          }
        } else {
          $('#k8s_connection').html('A challenge instance is already running.  You can only have one challenge instance running at a time.')
          $('#k8s_connection').css('display', 'block')
          $('#k8s_countdown').css('display', 'none')
          $('#k8s_start').css('display', 'none')
          $('#k8s_stop').css('display', 'none')
          $('#k8s_extend').css('display', 'none')
        }
      } else {
        $('#k8s_start').css('display', 'block')
        $('#k8s_stop').css('display', 'none')
        $('#k8s_connection').css('display', 'none')
        $('#k8s_countdown').css('display', 'none')
        $('#k8s_extend').css('display', 'none')
      }
  });
};
