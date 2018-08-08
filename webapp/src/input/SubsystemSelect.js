import React, {Component} from 'react';
import Select from 'react-select';
import axios from 'axios';

export default class SubsystemSelect extends Component {
  constructor(props) {
    super(props);
    this.state = {
      subsysReq: null,
      subsysOpts: [],
    };
  }

  componentWillMount = () => {
    this.loadSubsystems();
  }

  componentWillUnmount = () => {
    this.state.subsysReq && this.state.subsysReq.cancel();
    this.setState({
      subsysReq: null,
      subsysOpts: [],
    });
  };

  handleChange = change => {
    this.props.onChange(change.value);
  }

  loadSubsystems = () => {
    const source = axios.CancelToken.source();
    const p = axios
      .get('/cgi-bin/index.py', {
        params: {type: 'get_subsystems'},
        cancelToken: source.token,
      })
      .then(res => {
        if (res.data.error) throw res.data.error;
        return res.data.data.items.map(s => ({
          value: s.name,
          label: s.name,
        }));
      })
      .catch(err => {
        console.log(err);
        throw err;
      });
    p.cancel = () => source.cancel(`Cancelled request of type get_subsystems`);
    this.setState({subsysReq: p});

    p.then(res => {
      this.setState({subsysOpts: res, subsysReq: null});
    }).catch(err => {
      if (!axios.isCancel(err))
        this.setState({subsysOpts: [], subsysReq: null});
    });
  };

  render() {
    return (
      <Select
        placeholder="Select subsystem..."
        options={this.state.subsysOpts}
        value={{value: this.props.subsystem, label:this.props.subsystem}}
        onChange={this.handleChange}
        isLoading={this.state.subsysReq}
      />
    );
  }
}
