"""Q-Lambda source programs used by the SHA-520-r experiments."""

SHA520_SIGMA0_AND_CH = """
oracle sha520_sigma0_and_ch(x: qbit[64], y: qbit[64], z: qbit[64]) : qbit[64] {
    let sigma0: qbit[64] = (x >>> 28) ^ (x >>> 34) ^ (x >>> 39);
    with (
        let xy: qbit[64] = x & y;
        let not_x_z: qbit[64] = (~x) & z;
    ) do {
        let ch: qbit[64] = xy ^ not_x_z;
        let result: qbit[64] = sigma0 ^ ch;
    }
}
"""

SHA520_MESSAGE_SCHEDULE_WORD = """
oracle sha520_schedule_word(w2: qbit[64], w7: qbit[64], w15: qbit[64], w16: qbit[64]) : qbit[64] {
    let s0: qbit[64] = (w15 >>> 1) ^ (w15 >>> 8) ^ (w15 >> 7);
    let s1: qbit[64] = (w2 >>> 19) ^ (w2 >>> 61) ^ (w2 >> 6);
    let result: qbit[64] = s1 + w7 + s0 + w16;
}
"""
