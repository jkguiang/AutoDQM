import React from 'react';
import {Modal} from 'reactstrap';

export default function PlotModal({plot, ...modalProps}) {
  return (
    <Modal {...modalProps}>
      Testing
      {plot && <img src={plot.paths.png} alt="test" />}
    </Modal>
  );
}
