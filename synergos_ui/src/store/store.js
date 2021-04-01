import { createStore } from 'vuex';

export default createStore({
    state:{
        collab:'',
        project: '',
        expt: '',
        run: '',
        CNA: "https://www.channelnewsasia.com/news"
    },
    mutations: {
        
    },
    getters: {
        CNAurl: state => {
        return state.CNA + '/' + state.collab + '/' + state.run
        }
    },
    modules: {

    }
})