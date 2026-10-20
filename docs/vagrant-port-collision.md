# Vagrant port collision on macOS 26

**Symptom:** Windows molecule runs fail in `create` with `Vagrant found a port collision for the specified port and virtual machine. While this port was marked to be auto-corrected, the ports in the auto-correction range are all also used.` Linux runs in the same gate pass. `scripts/molecule.py` reports these runs as `HOST-SETUP`.

**Cause:** on macOS 26 with Vagrant 2.4.9 (embedded Ruby 3.3.8), a connect with a timeout (`Socket.tcp(..., connect_timeout:)`) reports every closed localhost port as open, while a blocking connect correctly gets `ECONNREFUSED`. Vagrant's forwarded-port collision check uses the timeout form, so every auto-corrected forward fails. Windows boxes need auto-correct for WinRM and RDP; Linux boxes forward only 22 → 2222, which is why they're unaffected. It is not the proxy, a stray VM, or a real listener.

**Fix (machine-local, once per controller):** create `~/.vagrant.d/Vagrantfile`, which Vagrant loads for every project, with a blocking-connect override:

```ruby
require "socket"

Vagrant::Util::IsPortOpen.module_eval do
  def is_port_open?(host, port)
    Socket.tcp(host, port).close
    true
  rescue Errno::ETIMEDOUT, Errno::ECONNREFUSED, Errno::EHOSTUNREACH, \
         Errno::ENETUNREACH, Errno::EACCES, Errno::ENOTCONN, Errno::EALREADY, \
         Errno::EADDRNOTAVAIL
    false
  end
end
```

Delete the override once a Vagrant release fixes the check. Each failed `create` leaves an unbooted VM behind; remove it with `vagrant destroy -f` from `~/.cache/molecule/extensions/<scenario>`.
