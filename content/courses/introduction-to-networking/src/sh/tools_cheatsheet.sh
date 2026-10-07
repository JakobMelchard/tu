#!/usr/bin/env bash
# tools_cheatsheet.sh — annotated networking command cheat sheet (note 11).
#
# Default is --dry-run: every command is printed, nothing is executed, no root
# needed.  `./tools_cheatsheet.sh --run <section>` executes the commands of one
# section (interfaces, routes, sockets, dns, trace, capture, nc).  Capture and
# traceroute need root (sudo) on most systems; the script says so and skips them
# when not root.  Linux commands (ip, ss) are shown next to the macOS/BSD
# equivalents (ifconfig, netstat) because the exercises may be solved on either.
set -euo pipefail

MODE="${1:---dry-run}"
SECTION="${2:-all}"
IFACE="${IFACE:-en0}"          # Linux: eth0/wlan0 — `ip link` lists them
TARGET="${TARGET:-tuwien.ac.at}"

run() {                        # run "explanation" command args...
  local why="$1"; shift
  printf '\n# %s\n$ %s\n' "$why" "$*"
  if [[ "$MODE" == "--run" ]]; then "$@" || printf '  (exit %s)\n' "$?"; fi
}
need_root() { [[ "$MODE" == "--run" && "$(id -u)" != 0 ]] && { echo "  (needs root: sudo $0 --run $1)"; return 1; }; return 0; }
want() { [[ "$SECTION" == all || "$SECTION" == "$1" ]]; }

want interfaces && {
  echo "== Interfaces: which L2/L3 addresses do I have?"
  run "Linux: links, MACs, state (UP/DOWN), MTU" ip link show
  run "Linux: IPv4/IPv6 addresses with prefix length and scope (global/link)" ip -br addr show
  run "macOS/BSD: same information (ether = MAC, inet = IPv4, inet6 = IPv6)" ifconfig "$IFACE"
  run "Linux: ARP / NDP neighbour cache (REACHABLE, STALE, FAILED)" ip neigh show
  run "macOS: ARP cache" arp -an
  run "macOS: IPv6 neighbour cache (NDP replaces ARP)" ndp -an
}

want routes && {
  echo "== Routes: how does the kernel forward (longest prefix match)?"
  run "Linux: routing table; 'default via' is 0.0.0.0/0" ip route show
  run "Linux: which route would be chosen for this destination (LPM lookup)" ip route get 1.1.1.1
  run "Linux IPv6 routing table" ip -6 route show
  run "macOS/BSD: routing table (-n = no DNS lookups)" netstat -rn
  run "macOS: single-destination lookup" route -n get 1.1.1.1
}

want sockets && {
  echo "== Sockets: who is listening / connected, TCP states"
  run "Linux: TCP+UDP listening sockets, numeric, with process" ss -tulpn
  run "Linux: all TCP connections with state (ESTAB, TIME-WAIT, SYN-SENT ...)" ss -tan
  run "macOS/BSD: same with netstat" netstat -an -p tcp
  run "macOS: which process owns which socket" lsof -nP -iTCP -sTCP:LISTEN
}

want dns && {
  echo "== DNS: dig is the exercise tool; +short for the answer only"
  run "A record, full answer with flags (qr rd ra ad) and sections" dig "$TARGET" A
  run "Only the answer" dig +short "$TARGET" AAAA
  run "Ask a specific resolver, request DNSSEC records (DO bit, prints RRSIG)" dig @1.1.1.1 +dnssec "$TARGET" A
  run "Follow the delegation chain from the root (shows the referral hierarchy)" dig +trace "$TARGET"
  run "Reverse lookup (PTR in in-addr.arpa)" dig -x 128.130.35.76
  run "Name servers and mail exchangers of a zone" dig "$TARGET" NS +short
  run "Authoritative answer straight from a zone's own server (aa flag)" dig +norecurse @ns1.tuwien.ac.at "$TARGET" SOA
  run "Query DNSKEY and DS to inspect the chain of trust" dig +dnssec "$TARGET" DNSKEY
  run "Plain host lookup via the system resolver (uses /etc/hosts, resolv.conf order)" getent hosts "$TARGET"
}

want trace && {
  echo "== Path discovery: TTL expiry -> ICMP time exceeded from each hop"
  need_root trace && run "traceroute with UDP probes (default), 3 probes per hop, no DNS" traceroute -n "$TARGET"
  need_root trace && run "ICMP echo probes instead (some firewalls only pass these)" traceroute -I "$TARGET"
  need_root trace && run "IPv6 path" traceroute6 -n "$TARGET"
  run "Reachability + RTT; -c 3 = three probes" ping -c 3 "$TARGET"
  run "Path MTU probe: 1472 B payload + 28 B headers = 1500; DF set (Linux: -M do, macOS: -D)" ping -c 1 -D -s 1472 "$TARGET"
}

want capture && {
  echo "== Packet capture: tcpdump (libpcap) and tshark (Wireshark CLI)"
  echo "   Filter language is BPF: host/net/port/proto/tcp[tcpflags] etc. -n no DNS, -v verbose, -X hex dump"
  need_root capture && run "Interfaces available to capture on" tcpdump -D
  need_root capture && run "10 packets on IFACE, no name resolution, with link-level header (-e shows MACs)" tcpdump -i "$IFACE" -n -e -c 10
  need_root capture && run "Only ARP" tcpdump -i "$IFACE" -n -c 5 arp
  need_root capture && run "TCP handshake segments only (SYN or FIN or RST set)" tcpdump -i "$IFACE" -n 'tcp[tcpflags] & (tcp-syn|tcp-fin|tcp-rst) != 0'
  need_root capture && run "DNS traffic to/from a resolver, verbose decode" tcpdump -i "$IFACE" -n -v 'udp port 53'
  need_root capture && run "ICMP (ping, traceroute answers)" tcpdump -i "$IFACE" -n icmp
  need_root capture && run "Write a pcap for later analysis (-s 0 = full packets)" tcpdump -i "$IFACE" -n -s 0 -w capture.pcap -c 100
  run "Read a pcap file (no root): absolute timestamps, hex+ascii" tcpdump -n -r capture.pcap -tttt
  run "tshark: read pcap, print selected fields as a table" tshark -r capture.pcap -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.flags -e tcp.seq -e tcp.ack
  run "tshark: display filter (Wireshark syntax, richer than BPF); tcp.analysis.* flags retransmissions" tshark -r capture.pcap -Y 'tcp.analysis.retransmission || tcp.analysis.duplicate_ack'
  run "tshark: follow one TCP conversation as a stream" tshark -r capture.pcap -q -z follow,tcp,ascii,0
  run "tshark: conversation statistics (who talked to whom, bytes)" tshark -r capture.pcap -q -z conv,tcp
  run "tshark: expand a whole packet tree for one frame" tshark -r capture.pcap -V -c 1
  echo "   Exercise workflow: capture -> filter to one flow (ip.addr==A && tcp.port==P) -> read seq/ack -> relative seq numbers off with -o tcp.relative_sequence_numbers:FALSE"
}

want nc && {
  echo "== nc/netcat: hand-made TCP and UDP endpoints"
  run "TCP listener on 9000 (-l listen, -k keep listening after a client leaves; macOS nc has no -k on all versions)" echo "nc -l 9000"
  run "TCP client: type, press enter, the bytes are delivered as a stream" echo "nc 127.0.0.1 9000"
  run "UDP endpoint (-u); datagram boundaries preserved" echo "nc -u -l 9001"
  run "Port scan / reachability check (-z no data, -v verbose)" echo "nc -zv $TARGET 80 443"
  run "Speak HTTP by hand (Telnet-style protocol probing)" echo "printf 'GET / HTTP/1.0\\r\\nHost: $TARGET\\r\\n\\r\\n' | nc $TARGET 80"
  run "Telnet client for negotiation observation (many systems: 'brew install telnet')" echo "telnet towel.blinkenlights.nl 23"
}

echo
echo "Mode: $MODE (use --run <section> to execute; sections: interfaces routes sockets dns trace capture nc)"
