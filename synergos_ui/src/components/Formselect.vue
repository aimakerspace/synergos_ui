<template>
    <form @submit.prevent="submitForm">
    <h3> Please fill in the following:</h3>
        <em class="dead_or_alive">Contacting backend... {{ ping_status }}</em>
        <br />
        <div class="nav">
             <br />
            <div class="nav_collab_header">
            <strong>Collaborations </strong>
            <div class="nav_collab_sel">
                <Multiselect
                v-model="nav_collab_m"
                :options="nav_collab_opt"
                ref="nav_multiselect_collab"
                @select="get_nav_project"
                @change="clear_nav_opt('projects')"
                ></Multiselect>
            </div>
            <br />
            </div>
            <div class="nav_project_header">
            <strong>Projects</strong>
            <div class="nav_project_sel">
                <Multiselect
                v-model="nav_project_m"
                :options="nav_project_opt"
                ref="nav_multiselect_project"
                @select="get_nav_expt"
                @change="clear_nav_opt('expts')"
                ></Multiselect>
            </div>
            <br />
            </div>
            <div class="nav_expt_header">
            <strong>Experiments</strong>
            <div class="nav_expt_sel">
                <Multiselect
                v-model="nav_expt_m"
                :options="nav_expt_opt"
                ref="nav_multiselect_expt"
                @select="get_nav_run"
                @change="clear_nav_opt('runs')"
                ></Multiselect>
            </div>
            <br />
            </div>
            <div class="nav_run_header">
            <strong>Runs</strong>
            <div class="nav_run_sel">
                <Multiselect
                v-model="nav_run_m"
                :options="nav_run_opt"
                ref="nav_multiselect_run"
                @select="get_run_metadata"
                ></Multiselect>
            </div>
            <br />
            <button>Submit</button>
            <p> {{collab}} </p>
        </div>
        </div>
    </form> 
</template>
   
<script>
import Multiselect from "@vueform/multiselect";
import "@vueform/multiselect/themes/default.css";
import axios from "axios";

export default {
   components: {
    Multiselect
  },
  props: {
    msg: String
  },
  computed: {
    nav_collab_opt() {
      const key_list = Object.keys(this.nav_collab_dict);
      console.log("collab keylist: ", key_list);
      let display_dict = {};
      for (const k of key_list) {
        display_dict[k] = k;
      }
      console.log("collab computed: ", display_dict);
      return display_dict;
    },
    nav_project_opt() {
      const key_list = Object.keys(this.nav_project_dict);
      console.log("project keylist: ", key_list);
      let display_dict = {};
      for (const k of key_list) {
        display_dict[k] = k;
      }
      console.log("project computed: ", display_dict);
      return display_dict;
    },
    nav_expt_opt() {
      const key_list = Object.keys(this.nav_expt_dict);
      console.log("expt keylist: ", key_list);
      let display_dict = {};
      for (const k of key_list) {
        display_dict[k] = k;
      }
      console.log("expt computed: ", display_dict);
      return display_dict;
    },
    nav_run_opt() {
      const key_list = Object.keys(this.nav_run_dict);
      console.log("run keylist: ", key_list);
      let display_dict = {};
      for (const k of key_list) {
        display_dict[k] = k;
      }
      console.log("run computed: ", display_dict);
      return display_dict;
    },
    has_metadata() {
      if (Object.keys(this.nav_run_metadata_dict).length > 0) {
        return true;
      } else {
        return false;
      }
    },
    
  },
  data() {
    return {
      ping_status: "failed! 😱",
      nav_collab_m: null,
      nav_project_m: null,
      nav_expt_m: null,
      nav_run_m: null,
      nav_collab_dict: { test: "test" },
      nav_project_dict: {},
      nav_expt_dict: {},
      nav_run_dict: {},
      nav_run_metadata_dict: {},
      project: '',
      expt: '',
      run: ''
    };
  },
  methods: {
    healthcheck() {
      const url = "http://localhost:12345/nav/ping";
      axios
        .get(url)
        .then(res => {
          this.ping_status = res.data;
        })
        .catch(error => {
          console.error(error);
        });
    },
    async get_nav_collab() {
      this.nav_collab_dict = await extract_nav_opts("collabs");
      console.log("get_nav_collabs: ", this.nav_collab_dict);
    },
    async get_nav_project() {
      console.log("get_nav_project, selected: ", this.nav_collab_m);
      const params = {
        collab_id: this.nav_collab_dict[this.nav_collab_m]
      };
      this.$store.state.collab = this.nav_collab_dict[this.nav_collab_m]
      console.log("get_nav_project, params: ", params);
      this.nav_project_dict = await extract_nav_opts("projects", params);
      console.log("get_nav_project: ", this.nav_project_dict);
    },
    async get_nav_expt() {
      console.log("get_nav_expt, selected: ", this.nav_project_m);
      const params = {
        project_id: this.nav_project_dict[this.nav_project_m]
      };
      this.$store.state.project = this.nav_project_dict[this.nav_project_m]
      console.log("get_nav_expt, params: ", params);
      this.nav_expt_dict = await extract_nav_opts("expts", params);
      console.log("get_nav_expt: ", this.nav_expt_dict);
    },
    async get_nav_run() {
      console.log("get_nav_run, selected: ", this.nav_expt_m);
      const params = {
        expt_id: this.nav_expt_dict[this.nav_expt_m]
      };
      this.$store.state.expt = this.nav_expt_dict[this.nav_expt_m]
      console.log("get_nav_run, params: ", params);
      this.nav_run_dict = await extract_nav_opts("runs", params);
      console.log("get_nav_run: ", this.nav_run_dict);
    },
    get_run_metadata() {
      console.log("get_run_metadata, select: ", this.nav_run_m);
      const params = {
        collab_id: this.nav_collab_dict[this.nav_collab_m],
        project_id: this.nav_project_dict[this.nav_project_m],
        expt_id: this.nav_expt_dict[this.nav_expt_m],
        run_id: this.nav_run_dict[this.nav_run_m]
      };
      this.$store.state.run = this.nav_run_dict[this.nav_run_m]
      console.log("get_run_metadata, params: ", params);

      const url = `http://localhost:12345/nav/run_metadata`;
      const config = {
        params: params
      };
      console.log(`calling run_metadata with config ${JSON.stringify(config)}`);
      axios
        .get(url, config)
        .then(res => {
          console.log(`response data: ${JSON.stringify(res.data)}`);
          this.nav_run_metadata_dict = res.data["results"];
          console.log("get_run_metadata: ", this.nav_run_metadata_dict);
          console.log("sources: ", this.nav_run_metadata_dict["sources"]);
        })
        .catch(error => {
          console.error(error);
        });    
        const fed = {
          fed: params          
        }
        console.log("fed", fed);       
        return fed
     },
     clear_nav_opt(nav_layer) {
      switch (nav_layer) {
        case "projects":
          this.$refs.nav_multiselect_project.clear();
          this.nav_project_dict = {};
          break;
        case "expts":
          this.$refs.nav_multiselect_expt.clear();
          this.nav_expt_dict = {};
          break;
        case "runs":
          this.$refs.nav_multiselect_run.clear();
          this.nav_run_dict = {};
          break;
        default:
          console.error("clear_nav_opt error!");
      }
    }
  },
  created() {
    this.healthcheck();
    this.get_nav_collab();
  }
};
async function extract_nav_opts(nav_layer, params = {}) {
  const valid_keys = ["collab_id", "project_id", "expt_id"];
  if (validate(params, valid_keys)) {
    const url = `http://localhost:12345/nav/${nav_layer}`;
    const config = {
      params: params
    };
    console.log(
      `calling nav_layer ${nav_layer} with config ${JSON.stringify(config)}`
    );
    const opt_dict = await axios
      .get(url, config)
      .then(res => {
        console.log(`response data: ${JSON.stringify(res.data)}`);
        let tmp_dict = {};
        res.data["results"][`${nav_layer}`].map(item => {
          tmp_dict[item.name] = item.id;
        });
        return tmp_dict;
      })
      .catch(error => {
        console.error(error);
      });
    return opt_dict
    }
  }
function validate(obj, arr) {
  return Object.keys(obj).every(e => arr.includes(e));
}
</script>
   
<style>
label {
  font-weight: bold;
  display: inherit;
  margin-bottom: 5px;
}
input + label {
  font-weight: bold;
  display: center;
  margin-right: 20px;
}
</style>