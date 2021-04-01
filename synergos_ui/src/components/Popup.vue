<template>
	<div class="popup">
		<div class="thumbnail">
            <h4> {{CNAurl}} </h4>   
            <a :href="`${CNAurl}`"> To webpage</a>
            <iframe :src="`${CNAurl}`"></iframe>
			<slot />
		</div>
	</div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
    setup(){
        const store = useStore()

        return {
            CNAurl: computed(() => store.getters.CNAurl)
        }
    }
}
</script>

<style lang="scss" scoped>
.thumbnail { /* the width and height here are your resultant sizes. */
    width: 400px;
    height: 300px;
    float:left;
    margin:20px;
    position: relative;
}
 
.thumbnail iframe {  /* the width and height here are your "unshrunken" sizes.  Important bc of the scale variable later. */
    position: relative;
    z-index: 1;
    width: 1000px;   
    height: 750px;
 
    -webkit-transform-origin: 0 0;
    -moz-transform-origin: 0 0;
    transform-origin: 0 0;

 
    -webkit-transform:  scale(0.4, 0.4);   /* Gets the size down to fit into your .thumbnail. */
    -moz-transform:  scale(0.4, 0.4);      /* Gets the size down to fit into your .thumbnail. */
    transform:  scale(0.4, 0.4);           /* Gets the size down to fit into your .thumbnail. */
    overflow: hidden;
    resize: both;

}

.thumbnail a {
    position: relative;
    top: 450px;
}
</style>