// groups

Vue.component('yapgroup', {
  props: ['group_pk', 'group_url', 'group_avatar_url', 'name', 'admin_url', 'admin_name', 'admin_is_user', 'activity_category', 'description', 'member_count', 'language_primary'],

  template: `
	<div class='group-div'>
		<div class="row">
			<div class="col-lg-3 text-center">
				<img :src="group_avatar_url" class="avatar-photo group-avatar group-avatar-grouplist" />
			</div>
			<div class="col-lg-9">
				<h3><a :href="group_url" >{{ name }}</a> <span v-if="admin_is_user" ><i class="fas fa-star text-warning"></i></span></h3>
				<b>Host: </b> 
				<a :href="admin_url" ><i class="fas fa-user-circle"></i> {{ admin_name }}</a>
				<br>

				<b>Category: </b> 
				{{ activity_category }}
				<br>

				<b>Language: </b> 
				{{ language_primary }}
				<br>

				<b>Description: </b> 
				{{ description }}
				<br><br>
				{{member_count}} Members
			</div>
		</div>
	</div>`
})


Vue.component('yapgrouptemplate', {
  props: ['all_groups_json'],

  template: `
  	<div id="group-div-container-template">
		<template v-if="all_groups_json.length">  
			<yapgroup
				v-for="group in all_groups_json"
				v-bind:key="group.group_pk"
				v-bind:group_url="group.group_url"
				v-bind:group_avatar_url="group.group_avatar_url"
				v-bind:name="group.name"
				v-bind:admin_url="group.admin_url"
				v-bind:admin_name="group.admin_name"
				v-bind:admin_is_user="group.admin_is_user"
				v-bind:activity_category="group.activity_category"
				v-bind:description="group.description"
				v-bind:member_count="group.member_count"
				v-bind:language_primary="group.language_primary"
			></yapgroup>

		</template >
		<template v-else>
			<h3 class="text-center" style="width:100%; margin: 30px;">No Groups.</h3>
		</template>
	</div>`
})



// events

Vue.component('yapevent', {
  props: ['event_pk', 'event_url', 'event_avatar_url', 'name', 'group_url', 'group_name', 'admin_url', 'admin_name', 'admin_is_user', 'start_time', 'description', 'language_primary', 'attendee_count', 'maximum_attendee_count', 'time_until_event_start'],

  template: `
	<div class="event-div row">
		<div class="col-lg-2">
			<table style="height:100%;"><tr><td style="vertical-align:middle; height: 100%;">
				<h5 class='text-center'>{{ start_time }}</h5>
				<p class="text-center text-info">{{ time_until_event_start }}</p>
			</td></tr></table>
		</div>
		<div class="col-lg-7">
			<h3><a :href="event_url" >{{ name }}</a> <span v-if="admin_is_user" ><i class="fas fa-star text-warning"></i></span></h3>
			<b>Group: </b> <a :href="group_url" ><i class="fas fa-users"></i> {{ group_name }}</a>
			<br>

			<b>Host: </b> <a :href="admin_url" ><i class="fas fa-user-circle"></i> {{ admin_name }}</a>
			<br>

			<b>Language: </b> 
			{{ language_primary }}
			<br>

			<b>Description:</b> 
			{{ description }}
			<br><br>

			{{ attendee_count }} Attendees <span class="ml-3 text-nowrap">(max {{ maximum_attendee_count }})<span>
		</div>
		<div class="col-lg-3 text-center p-2">
				<img :src="event_avatar_url" class="avatar-photo event-avatar event-avatar-eventlist" />
		</div>
	</div>`
})



Vue.component('yapeventtemplate', {
  props: ['all_events_json'],

  template: `
  	<div id="event-div-container-template">
		<template v-if="all_events_json.length">  

			<yapevent
				v-for="event in all_events_json"
				v-bind:key="event.event_pk"
				v-bind:event_url="event.event_url"
				v-bind:event_avatar_url="event.event_avatar_url"
				v-bind:name="event.name"
				v-bind:group_url="event.group_url"
				v-bind:group_name="event.group_name"
				v-bind:admin_url="event.admin_url"
				v-bind:admin_name="event.admin_name"
				v-bind:admin_is_user="event.admin_is_user"
				v-bind:start_time="event.start_time"
				v-bind:description="event.description"
				v-bind:language_primary="event.language_primary"
				v-bind:attendee_count="event.attendee_count"
				v-bind:maximum_attendee_count="event.maximum_attendee_count"
				v-bind:time_until_event_start="event.time_until_event_start"
			></yapevent>

		</template >
		<template v-else>
			<h3 class="text-center" style="width:100%; margin: 30px;">No Events.</h3>
			<br>
		</template>
	</div>`
})






// posts


Vue.component('yappost', {
  props: ['post_pk', 'poster_url', 'profile_avatar_micro_url', 'poster_name', 'post_text', 'created_at'],

  template: `
	<div class="post-div">
		<div class="post-container">
		    <img :src="profile_avatar_micro_url" class="yapprofile-list-image" /> <b><a :href="poster_url" >{{ poster_name }}</a></b>
		    <br>
		    <pre>{{ post_text }}</pre>
		    <span class="time-right">{{ created_at }}</span>
		</div>
	</div>`
})



Vue.component('yapposttemplate', {
  props: ['all_posts_json'],

  template: `
  	<div id="post-div-container-template">
		<template v-if="all_posts_json.length">  

			<yappost
				v-for="post in all_posts_json"
				v-bind:key="post.post_pk"
				v-bind:poster_url="post.poster_url"
				v-bind:profile_avatar_micro_url="post.profile_avatar_micro_url"
				v-bind:poster_name="post.poster_name"
				v-bind:post_text="post.post_text"
				v-bind:created_at="post.created_at"
			></yappost>

		</template >
		<template v-else>
			<h3 class="text-center" style="width:100%; margin: 30px;">No Posts.</h3>
			<br>
		</template>
	</div>`
})



// profiles


Vue.component('yapprofile', {
  props: ['profile_pk', 'profile_url', 'profile_name', 'profile_avatar_micro_url'],
  template: `<div class="yapprofile-list-div"><img :src="profile_avatar_micro_url" class="yapprofile-list-image" /> <a :href="profile_url" target="_blank" >{{ profile_name }}</a></div>`
})



Vue.component('yapprofiletemplate', {
  props: ['all_profiles_json'],

  template: `
  	<div id="profile-div-container-template">
		<template v-if="all_profiles_json.length">  
				<yapprofile
					v-for="profile in all_profiles_json"
					v-bind:key="profile.profile_pk"
					v-bind:profile_url="profile.profile_url"
					v-bind:profile_name="profile.profile_name"
					v-bind:profile_avatar_micro_url="profile.profile_avatar_micro_url"
				></yapprofile>

		</template >
		<template v-else>
			<h3 class="text-center" style="width:100%; margin: 30px;">No users signed up.</h3>
			<br>
		</template>
	</div>`
})






// show "top" button when user scrolls down
function scrollFunction() {
    var topButton = document.getElementById("topButton");
    if (topButton === null) {return;}

    if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
        topButton.style.display = "block";
        $("#maindiv").css("padding-bottom", "100px");
    } else {
        topButton.style.display = "none";
    }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {
  scrollFunction();
}
