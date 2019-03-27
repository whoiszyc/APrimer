function a = LSclass(varargin)
% constructor of the class Lines
% == Lines ==

global Settings

switch nargin
 case 0
  a.con = [];
  a.n = 0;
  a.bus1 = [];
  a.bus2 = [];
  a.v1 = [];
  a.v2 = [];
  a.store = [];
  a.u = [];
  a.ncol = 9;
  a.format = ['%4d %4d ',repmat('%8.5g ',1,6),'%2u'];
  if Settings.matlab, a = class(a,'LSclass'); end
 case 1
  if isa(varargin{1},'LSclass')
    a = varargin{1};
  else
    error('Wrong argument type')
  end
 otherwise
  error('Wrong Number of input arguments')
end
