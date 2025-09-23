/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
<<<<<<<< HEAD:superset-frontend/packages/superset-ui-chart-controls/src/utils/colorControls.ts
export const getColorControlsProps = (state: Record<string, any>) => {
  const dashboardId = state?.form_data?.dashboardId;
  return {
    chartId: state?.slice?.slice_id,
    dashboardId,
    hasDashboardColorScheme:
      !!dashboardId && !!state?.form_data?.dashboard_color_scheme,
    hasCustomLabelsColor:
      Object.keys(state?.form_data?.label_colors || {}).length > 0,
    colorNamespace: state?.form_data?.color_namespace,
    mapLabelsColors: state?.form_data?.map_label_colors || {},
    sharedLabelsColors: state?.form_data?.shared_label_colors || [],
  };
};
========
import { render, screen } from 'spec/helpers/testing-library';
import { ListProps } from 'antd-v5/lib/list';
import { List } from '.';

const mockedProps: ListProps<any> = {
  dataSource: ['Item 1', 'Item 2', 'Item 3'],
  renderItem: item => <div>{item}</div>,
};

test('should render', () => {
  const { container } = render(<List {...mockedProps} />);
  expect(container).toBeInTheDocument();
});

test('should render the correct number of items', () => {
  render(<List {...mockedProps} />);

  const listItemElements = screen.getAllByText(/Item \d/);

  expect(listItemElements.length).toBe(3);
  listItemElements.forEach((item, index) => {
    expect(item).toHaveTextContent(`Item ${index + 1}`);
  });
});
>>>>>>>> 5.0.0:superset-frontend/src/components/List/List.test.tsx
