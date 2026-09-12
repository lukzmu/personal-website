Title: Raspberry Pi, NixOS and Home Assistant. A survival story.
Date: 2026-08-26 10:00
Model: opus
Tool: claude

Recently, due to the doings and politics of the USA government, I started moving more and more of my services outside of their Big Tech companies, to focus on [european alternatives](https://european-alternatives.eu/) and [open source software](https://opensourcealternative.to/). I doubt they would pull the plug on Europe, because there's too much money invested by these corporations, but I generally like the idea of keeping my information private, while doing some nerdy work around it. 

My `nix-config` repository had exactly one host since I made the Linux jump: `sol`, the desktop I work on. The plan was to add a second one - `luna`, a headless Raspberry Pi 5 running Home Assistant - and it looked like maybe 1-2 evenings of work. Copy the host directory, change the architecture, deploy, done.

Frankly, it was not. It was several evenings, one entire lost day staring at a Pi that refused to boot, and a thermometer that toyed with me with 4 separate issues before it would report the temperature outside my window.

What follows is the list of things I actually learned, in roughly the order they hurt. The code is in [nix-config](https://github.com/lukzmu/nix-config) if you want to read the finished version rather than the endless technological suffering.

## What I was actually building

`luna` is a Raspberry Pi 5 with 8 GB of RAM, booting from a 32 GB class-10 microSD, with no SSD attached (this is something I want to change in the future, because running it on a microSD is generally a bad idea. I just didn't want to spend too much money to begin with). It runs Home Assistant in rootful Podman, alongside an OpenThread Border Router and a Matter server, so that a Thread-based Eve Weather sensor has something to talk to.

Nothing gets built on the Pi itself - no point starving a modest board and a microSD card with compile jobs. `sol` builds the whole `aarch64` closure using `boot.binfmt.emulatedSystems` and pushes it over SSH. Since it's on NixOS I had to carefully look at ownership as this was a problem for me in the past:

| Path | Owner | Contents |
| --- | --- | --- |
| `hosts/luna/home-assistant/` | Nix, in this repo | Compose file, service definitions, capabilities |
| `/var/lib/home-assistant/` | Runtime state | Thread creds, Matter fabric, integrations |
| `secrets.env` | Myself with `0600` | Credentials that must not enter any store |
| `~/.config/home-assistant` | A separate git repo | Home Assistant's own YAML, automations, dashboards |

I'll come back to why that table matters more than it looks.

## The kernel gamble that paid off

`nixos-hardware` has a `raspberry-pi-5` module, and importing it is obviously the right move. What is less obvious is that it defaults to Raspberry Pi's own downstream kernel tree, and **no binary cache serves that kernel**. On an x86 machine building for ARM through qemu emulation, that is not a download - it is a multi-hour compile of a Linux kernel running under an instruction translator.

So I overrode it:

```nix
{
  imports = [inputs.nixos-hardware.nixosModules.raspberry-pi-5];
  boot.kernelPackages = pkgs.linuxPackages;
}
```

Mainline 6.18 does carry BCM2712 and RP1 support now, and it comes straight out of `cache.nixos.org`. `luna`'s kernel resolved to `linux-6.18.43` and was fetched, not built. Only a few cheap module-repackaging derivations ran locally.

There was one trap hiding underneath it. On a Pi 5, both USB and Ethernet hang off **RP1**, a southbridge sitting behind the BCM2712 PCIe root complex. Inspecting the built module tree showed `xhci-pci`, `usb_storage` and `macb` were compiled in, but `pcie-brcmstb` and `rp1-pci` were *modules*, and they were not in the initrd. Boot from any USB medium and the root filesystem was unreachable, because the bus it lives on never came up.

```nix
boot.initrd.availableKernelModules = [
  "pcie-brcmstb"
  "rp1-pci"
  "usbhid"
  "usb_storage"
  "uas"
];
```

The incidental win: `macb` being built into mainline is what confirmed ethernet would work at all. That was the single biggest risk in the whole plan, and it evaporated by reading a module tree instead of by rebooting hopefully.

**Lesson:** when a hardware module "just works", find out *which* kernel it decided you wanted. And check what the initrd actually contains before trusting that your root device is reachable.

## The day the Pi died

Then it stopped booting. Green LED, no DHCP lease, no network, nothing on the wire.

It had booted fine an hour earlier, so this was concerning.

I burned an entire day on three hypotheses, and all three were wrong:

1. **My configuration broke it.** I rolled the extlinux entry back to the stock generation. Apparently it's not always my shitty code fault.
2. **The ext4 resize corrupted the card.** It took ages to even land on this one. I wrote a completely fresh, unresized image - identical failure.
3. **The device tree or networkd was wrong.** The filtered DTB turned out byte-identical to the kernel's and correctly described `raspberrypi,rp1-gem`. The networkd unit had the right `en*` match. Both fine.

The actual fault was the **Raspberry Pi 5 bootloader EEPROM**. Not the card, not NixOS, not my config - the firmware living on the board itself. The fix is a recovery flash: put `recovery.bin` plus a `pieeprom.upd` and its `pieeprom.sig` (generated with `rpi-eeprom-digest`) onto the FAT boot partition and power-cycle. `recovery.bin` renames itself to `RECOVERY.000` when it succeeds, which is the only honest confirmation that it ran.

A nixpkgs-specific wrinkle: `rpiboot` ships only the `msd` and `mass-storage-gadget64` payloads, with no recovery payload at all. The Pi 5 bootloader images live in `raspberrypi-eeprom` under `bootloader-2712/`, so the recovery directory has to be assembled by hand from two packages.

::: chat Anna
You said *"I'll just plug in the sensor"* on Saturday morning.
:::

::: chat Łukasz
And I did plug it in. Nobody said anything about it working.
:::

Two diagnostic lessons came out of this, and they cost more than the fix did.

The first: **`rpiboot` kept working the entire time**. The board was demonstrably alive and talking over USB while it refused to boot. That single fact isolates "boot path fault" from "dead board", and I should have weighted it far more heavily than I did instead of rewriting the card again.

The second is worse, because I did it to myself. I had set journald to volatile storage to spare the microSD:

```nix
services.journald.extraConfig = ''
  Storage=volatile
  RuntimeMaxUse=64M
'';
```

Which means every failed boot destroyed its own evidence. A headless machine with no persistent logs cannot tell you why it didn't come up, and that is precisely the failure a headless machine has. For debugging purposes I set `Storage=persistent` with a sizeable cap, and it helped a lot.

While I was chasing ghosts I also kept scanning the LAN filtered by Raspberry Pi MAC OUI, and kept finding nothing - because NixOS with NetworkManager presents a randomised, locally-administered MAC. The router's own DHCP client list found it every single time. Fancy tooling lost to the boring list.

## The card is the part that dies

A Raspberry Pi on a microSD has one obvious mortality risk, and it is not the CPU. Every avoidable write shortens the card's life, so `luna`'s config treats writes as a budget:

```nix
swapDevices = [];
zramSwap.enable = true;
```

No swap file, because on a machine with no SSD the swap file would be the single hottest write target on the card. Compressed RAM instead. On top of that: `boot.tmp.useTmpfs`, documentation disabled, weekly garbage collection with a 14-day window, `configurationLimit = 5` on the bootloader, and `i18n.supportedLocales` trimmed to three entries - the full `glibc-locales` was both the slowest emulated build in the closure and roughly 200 MB of a 32 GB card.

The other half of that budget is not in Nix at all. Home Assistant's recorder writes every state change to SQLite by default, which on an appliance full of chatty sensors is a continuous write stream. Its `configuration.yaml` gets a `recorder:` block that keeps a week of history, batches commits every 30 seconds, and excludes the entities that churn for no reason - signal strength, link quality, uptime, `sun.sun`.

```yaml
recorder:
  purge_keep_days: 7
  commit_interval: 30
  auto_purge: true
  auto_repack: true
  exclude:
    domains:
      - camera
      - update
    entities:
      - sun.sun
    entity_globs:
      - sensor.*_linkquality
      - sensor.*_rssi
      - sensor.*_lqi
      - sensor.*_signal_strength
      - sensor.*_last_seen
      - sensor.*_uptime
```

## Flashing a radio without Home Assistant OS

The Eve Weather sensor I own is a Thread device, so the Pi needs a Thread border router, so the ZBT-2 dongle needs OpenThread RCP firmware rather than the Zigbee firmware it ships with.

::: chat Łukasz
Fun fact, at first I actually ordered the wrong dongle by mistake (ZWA-2) and ZBT-2 still arrived faster.
:::

Nabu Casa's official flow for this runs inside Home Assistant OS. `luna` does not run Home Assistant OS - it runs NixOS with Home Assistant in a container - so that path was closed before it opened. The dongle got flashed from `sol` instead, using the web flasher at `toolbox.openhomefoundation.org`, which drives the radio over **WebSerial** - so it needs a Chromium-based browser, a requirement I got for free by already using Brave and would otherwise have walked straight into.

And that is where NixOS put up a wall I did not expect. Serial devices are `root:dialout` mode `0660`, and NixOS ships **no `uaccess` ACL rule** for them - the only udev rule granting a logged-in user direct access to a serial device covers a single Valve product. So the browser could see nothing at all until my user was in `dialout`:

```nix
extraGroups = [
  # ...
  # Serial adapters are root:dialout 0660 and get no uaccess ACL,
  # so this is what lets the user reach the ZBT-2 at all:
  # on sol to flash firmware, on luna to debug a radio.
  "dialout"
];
```

Group membership is fixed when your session starts, so this needs a full logout and login, not a rebuild. If you would rather stay on the command line, `universal-silabs-flasher` *is* in nixpkgs, with a `--profile zbt2` that knows the ZBT-2's layout.

## Containers that lie to you

Three separate container problems, all of the same shape: the image did not behave the way its documentation implied.

**The archived project.** I was ready to run `python-matter-server`, which is what half the internet still tells you to use. It was archived after 8.1.2, and its `stable` tag is now the final build of a dead project rather than a maintained image - the sort of thing that looks perfectly healthy in `docker pull` and rots quietly. Home Assistant's own container documentation points at `matterjs-server` now. Worth noting that a container registry has no concept of "this project is over".

**The user ID.** `matterjs-server` declares `"User": "1000:1000"`, unlike the root-run server it replaces. Rootful Podman maps container uid 1000 straight through to host uid 1000, so my perfectly sensible root-owned state directory was an instant `EACCES` crash loop:

```nix
# matterjs-server runs as uid 1000, unlike the root-run python server it
# replaced, so a root-owned directory is an EACCES crash loop on startup.
"d ${stateDir}/matter 0700 1000 1000 - -"
```

**The symlink.** The OpenThread Border Router entrypoint runs `mkdir -p /data/thread` followed by `ln -sft /var/lib /data/thread`. It wants to *create* `/var/lib/thread` as a symlink. Bind-mount a directory there - which is exactly what the path name invites you to do - and that `ln` fails, and `otbr-agent` exits before it ever opens the radio. The mount belongs on the other side of the link:

```yaml
volumes:
  - /var/lib/home-assistant/otbr:/data/thread
```

One habit that saved time rather than costing it: every image in this stack was checked with `skopeo inspect --raw` for a `linux/arm64` manifest *before* the Pi ever tried to pull it. On ARM, "the image exists" and "the image runs" are different claims.

## Profiles, and the orphan that wasn't

Not every radio is always plugged in, so the radio services sit behind docker-compose **profiles**, driven from Nix:

```nix
# Possible values: thread, zwave, eufy
enabledServices = ["thread"];
```

```nix
composeEnv = pkgs.writeText "home-assistant-compose.env" ''
  COMPOSE_PROFILES=${lib.concatStringsSep "," enabledServices}
  # ...
'';
```

Drop an entry from that list and the container is parked, so the stack still comes up cleanly with a dongle missing. Very tidy.

Except it did not stay tidy. I found `matter-server` running happily on a host where `enabledServices` was `[]`, which for a declarative configuration is about as unwelcome as it gets. The cause is a genuinely subtle one: `docker-compose up --remove-orphans` removes services that were **deleted from the file**. It does not stop a service that is still declared but whose profile just went inactive. Combine that with `restart: unless-stopped` and the container cheerfully resurrected itself on every boot, permanently out of sync with the file that was supposed to define it.

**Lesson:** `--remove-orphans` sounds like "make reality match the file". It means something considerably narrower, and the gap between those two readings is where configuration drift lives.

## What belongs in Nix, and what genuinely does not

The strong temptation with a setup like this is to put *everything* in the flake. That is the wrong instinct, and the split ended up being three-way rather than two.

**Nix owns the shape of the system**: the compose file, the generated environment, the udev rules, the `tmpfiles` declarations, the systemd unit.

**Home Assistant owns its own configuration**, in a separate git repository bind-mounted as `/config`. Automations and dashboards are edited through a web UI often - pretending they are declarative just means fighting the application.

**Secrets belong in neither.** The Nix store is world-readable and in my public git repository. Credentials live in a root-owned `0600` file outside both repositories, and the unit simply refuses to start without it:

```nix
unitConfig.ConditionPathExists = lib.mkIf needsSecrets secretsEnv;
```

A fresh deploy without credentials fails visibly instead of crash-looping a container that will never authenticate.

## Thermometer, Y U NO WORK

I decided to start with the Eve Weather device, as it seemed the easiest to pair. "Seemed" is a horrible assumption.

With the border router reporting `leader` and the Matter server listening, pairing one battery-powered temperature sensor should have been the easy part.

It was not. In order:

1. **The phone app scanned the QR code and failed.** The device was still paired to Apple Home, so it was not advertising for commissioning at all. A HomeKit or Matter accessory serves one controller. Ten seconds on the reset button, the display said `Hi`, and it started advertising.
2. **The phone-side flow still failed** with a cheerfully unhelpful "can't add the accessory". Switching to browser-based commissioning moved the work server-side, so the Pi's own Bluetooth radio ran the process - and, crucially, so the logs were on a machine I could read.
3. **That died partway through commissioning**, with the following statement in the logs: `[wifi-or-thread-network-credentials-not-configured]`. Which was baffling, because Home Assistant's own stored Thread datasets clearly showed a preferred network. It had the credentials. It just never handed them over - the Matter server's greeting reported `thread_credentials_set: false` throughout.
4. **Fixed by hand.** Pull the active dataset out of the border router's REST API, pipe it into the Matter server's `set_thread_dataset` call over its websocket, and the flag flips to `true`. Commissioning then succeeded on the next attempt and the node joined the fabric.

If you do this yourself: that dataset TLV **contains your Thread network key**. It is the credential for your entire mesh. Do not paste it into a forum thread, an issue, or a chat window while asking for help - redact it first.

The honest read on step 3 is that "drop-in replacement" was doing some heavy lifting. Same port, same websocket path, same protocol version - and one initialisation call that nothing made.

## Shooting my own foot

The best bug of the whole exercise was mine.

I had written a small `ha` helper into the config - `up`, `down`, `restart`, `logs`, `ps` - which drives the systemd unit that owns the whole compose project. Right after commissioning finally succeeded, I ran `ha restart`.

That restarted **everything**, including the border router. Which destroyed and recreated `wpan0` - the interface index went from 4 to 6, which is how I eventually spotted it - which dropped the IPv6 route to the Thread mesh. The Matter server started logging `ENETUNREACH` to the sensor's address, its subscription timed out, and the device I had just spent an evening pairing went `unavailable`.

The mesh itself survived; the off-mesh-routable prefix was unchanged afterwards, so the Thread network never re-formed. It was purely a routing casualty of restarting a container that had no business being restarted.

The helper is too coarse. "Restart Home Assistant" and "restart the radio stack that Home Assistant depends on" are different operations that should never have shared a verb, and the convenience wrapper hid that from me right up until it bit. A helper script that makes the dangerous thing as easy as the safe thing is not a helper.

## Summary

The finished setup is genuinely good. One command rebuilds and deploys the whole appliance from `sol`, the container stack is declared in a reviewable file, radios can be added or parked by editing a list, and the parts that should not be declarative - Home Assistant's own config, and the secrets - are honestly kept out of it.

But almost none of the difficulty was where I expected it. The Nix side was the *easy* part; the module refactor to make shared code architecture-neutral took an afternoon and `nix store diff-closures` proved my desktop was untouched by it. Everything expensive lived one layer below or one layer above: board firmware, initrd contents, a container's uid, an entrypoint's symlink, an initialisation call that quietly never happened.

Three things I'd take to the next box, in order of how much they cost me:

- **Keep the logs.** Optimising away your own post-mortem evidence is a false economy, and you find that out on the day you need it.
- **Notice what still works.** `rpiboot` responding the whole time was the answer, sitting in plain view, while I reimaged a card that was never broken.
- **Read the entrypoint.** For anything running in a container that touches devices, networking or state directories, the shell script that starts it will tell you more in two minutes than the README will in twenty.

The outside temperature is 21.4 degrees, and I know exactly why.
