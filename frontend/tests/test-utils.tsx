import { render, type RenderOptions } from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';
import { useReducer } from 'react';
import { AppContext, appReducer, initialState, type AppState } from '../src/state/appState';
import { MOCK_LAB } from '../src/data/mockLab';

export function createLoadedState(overrides: Partial<AppState> = {}): AppState {
  return {
    ...initialState,
    loading: false,
    lab: MOCK_LAB,
    events: MOCK_LAB.events,
    fromMock: true,
    ...overrides,
  };
}

function TestAppProvider({
  children,
  initial,
}: {
  children: ReactNode;
  initial?: Partial<AppState>;
}) {
  const [state, dispatch] = useReducer(appReducer, createLoadedState(initial));
  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
}

export function renderWithApp(
  ui: ReactElement,
  options?: RenderOptions & { initial?: Partial<AppState> },
) {
  const { initial, ...rest } = options ?? {};
  return render(ui, {
    wrapper: ({ children }) => <TestAppProvider initial={initial}>{children}</TestAppProvider>,
    ...rest,
  });
}
