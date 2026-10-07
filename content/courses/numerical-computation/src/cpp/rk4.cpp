// Classical RK4 [S4 §9.3.1] (CSE) and adaptive RK45 (Dormand-Prince, [S19],
// beyond [S4]) on test ODEs; note 11.
// State vectors are std::vector<double>; f(t, y) returns dy/dt.
// Build: make; run: ./rk4
#include <cmath>
#include <cstdio>
#include <functional>
#include <vector>

#include "check.hpp"

using Vec = std::vector<double>;
using Rhs = std::function<Vec(double, const Vec&)>;

Vec axpy(const Vec& y, double h, const Vec& k) {  // y + h k
    Vec r(y.size());
    for (size_t i = 0; i < y.size(); ++i) r[i] = y[i] + h * k[i];
    return r;
}

// One classical RK4 step: k1..k4, y += h/6 (k1 + 2k2 + 2k3 + k4).  Order 4.
Vec rk4_step(const Rhs& f, double t, const Vec& y, double h) {
    Vec k1 = f(t, y);
    Vec k2 = f(t + h / 2, axpy(y, h / 2, k1));
    Vec k3 = f(t + h / 2, axpy(y, h / 2, k2));
    Vec k4 = f(t + h, axpy(y, h, k3));
    Vec r(y.size());
    for (size_t i = 0; i < y.size(); ++i) r[i] = y[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    return r;
}

Vec rk4(const Rhs& f, double t0, Vec y, double h, int n) {
    for (int k = 0; k < n; ++k) y = rk4_step(f, t0 + k * h, y, h);
    return y;
}

// Dormand-Prince 5(4): 7 stages (FSAL), embedded 4th-order solution for the
// error estimate.  Step accepted when err = max_i |y5_i - y4_i| / (atol + rtol max(|y_i|, |y5_i|)) <= 1;
// next h = h * clamp(0.9 err^(-1/5), 0.2, 5).
struct RK45Result { Vec y; int steps, rejected; double hmin, hmax; };

RK45Result rk45(const Rhs& f, double t, Vec y, double t_end, double rtol, double atol) {
    static const double c[] = {0, 1. / 5, 3. / 10, 4. / 5, 8. / 9, 1, 1};
    static const double a[7][6] = {
        {},
        {1. / 5},
        {3. / 40, 9. / 40},
        {44. / 45, -56. / 15, 32. / 9},
        {19372. / 6561, -25360. / 2187, 64448. / 6561, -212. / 729},
        {9017. / 3168, -355. / 33, 46732. / 5247, 49. / 176, -5103. / 18656},
        {35. / 384, 0, 500. / 1113, 125. / 192, -2187. / 6784, 11. / 84}};
    static const double b5[] = {35. / 384, 0, 500. / 1113, 125. / 192, -2187. / 6784, 11. / 84, 0};
    static const double b4[] = {5179. / 57600, 0, 7571. / 16695, 393. / 640, -92097. / 339200, 187. / 2100, 1. / 40};

    const size_t d = y.size();
    double h = 0.01 * (t_end - t);
    RK45Result res{y, 0, 0, 1e300, 0.0};
    Vec k[7];
    k[0] = f(t, y);
    while (t < t_end) {
        h = std::min(h, t_end - t);
        for (int s = 1; s < 7; ++s) {
            Vec ys = y;
            for (int j = 0; j < s; ++j)
                for (size_t i = 0; i < d; ++i) ys[i] += h * a[s][j] * k[j][i];
            k[s] = f(t + c[s] * h, ys);
        }
        Vec y5 = y, y4 = y;
        for (int s = 0; s < 7; ++s)
            for (size_t i = 0; i < d; ++i) { y5[i] += h * b5[s] * k[s][i]; y4[i] += h * b4[s] * k[s][i]; }
        double err = 0.0;
        for (size_t i = 0; i < d; ++i)
            err = std::max(err, std::fabs(y5[i] - y4[i]) / (atol + rtol * std::max(std::fabs(y[i]), std::fabs(y5[i]))));
        if (err <= 1.0) {
            t += h; y = y5; k[0] = k[6];          // FSAL
            ++res.steps;
            res.hmin = std::min(res.hmin, h); res.hmax = std::max(res.hmax, h);
        } else {
            ++res.rejected;
        }
        const double fac = err > 0 ? 0.9 * std::pow(err, -0.2) : 5.0;
        h *= std::min(5.0, std::max(0.2, fac));
    }
    res.y = y;
    return res;
}

int main() {
    // 1. y' = -2 t y, y(0) = 1 -> y(t) = exp(-t^2): RK4 global error is O(h^4)
    {
        Rhs f = [](double t, const Vec& y) { return Vec{-2 * t * y[0]}; };
        const double exact = std::exp(-4.0);
        const double e1 = std::fabs(rk4(f, 0.0, {1.0}, 2.0 / 40, 40)[0] - exact);
        const double e2 = std::fabs(rk4(f, 0.0, {1.0}, 2.0 / 80, 80)[0] - exact);
        std::printf("RK4 on y' = -2ty: error h=1/20: %.3e, h=1/40: %.3e, observed order %.3f\n",
                    e1, e2, std::log2(e1 / e2));
        CHECK_LESS(e1, 1e-6);
        CHECK_NEAR(std::log2(e1 / e2), 4.0, 0.15);
    }
    // 2. harmonic oscillator y'' = -y as a system, energy drift of RK4 is tiny
    {
        Rhs f = [](double, const Vec& y) { return Vec{y[1], -y[0]}; };
        Vec y = rk4(f, 0.0, {1.0, 0.0}, 0.01, 1000);
        const double E = 0.5 * (y[0] * y[0] + y[1] * y[1]);
        std::printf("oscillator at t=10: y = (%.10f, %.10f), exact (%.10f, %.10f), energy %.12f\n",
                    y[0], y[1], std::cos(10.0), -std::sin(10.0), E);
        CHECK_NEAR(y[0], std::cos(10.0), 1e-8);
        CHECK_NEAR(y[1], -std::sin(10.0), 1e-8);
        CHECK_NEAR(E, 0.5, 1e-9);
    }
    // 3. stability: y' = -50 y with h = 0.1 (z = -5, outside |R(z)| <= 1) blows up,
    //    h = 0.05 (z = -2.5, inside the RK4 interval [-2.785, 0]) decays
    {
        Rhs f = [](double, const Vec& y) { return Vec{-50.0 * y[0]}; };
        const double blow = rk4(f, 0.0, {1.0}, 0.1, 20)[0];
        const double ok = rk4(f, 0.0, {1.0}, 0.05, 40)[0];
        const double R = 1 - 5 + 12.5 - 125. / 6 + 625. / 24;  // R(-5) for RK4
        std::printf("stiff test: |y_20| with z=-5: %.3e (R(-5)^20 = %.3e), with z=-2.5: %.3e\n",
                    std::fabs(blow), std::pow(R, 20), std::fabs(ok));
        CHECK_NEAR(blow, std::pow(R, 20), 1e-6 * std::pow(R, 20));
        CHECK_LESS(std::fabs(ok), 1e-3);
    }
    // 4. adaptive RK45 on the Van der Pol oscillator (mu = 5): step sizes vary widely
    {
        const double mu = 5.0;
        Rhs vdp = [mu](double, const Vec& y) { return Vec{y[1], mu * (1 - y[0] * y[0]) * y[1] - y[0]}; };
        RK45Result r = rk45(vdp, 0.0, {2.0, 0.0}, 20.0, 1e-8, 1e-10);
        // reference: RK4 with a very small fixed step
        Vec ref = rk4(vdp, 0.0, {2.0, 0.0}, 1e-4, 200000);
        std::printf("Van der Pol mu=5, t=20: RK45 %d steps (%d rejected), h in [%.1e, %.1e]\n",
                    r.steps, r.rejected, r.hmin, r.hmax);
        std::printf("  y = (%.10f, %.10f), fixed-step RK4 reference (%.10f, %.10f)\n", r.y[0], r.y[1], ref[0], ref[1]);
        CHECK_NEAR(r.y[0], ref[0], 1e-6);
        CHECK_NEAR(r.y[1], ref[1], 1e-6);
        CHECK_LESS(r.hmin / r.hmax, 0.2);        // the controller really adapts
        CHECK_LESS(static_cast<double>(r.steps), 200000.0 / 50);
    }
    // 5. RK45 on the smooth problem needs few steps for a tight tolerance
    {
        Rhs f = [](double t, const Vec& y) { return Vec{-2 * t * y[0]}; };
        RK45Result r = rk45(f, 0.0, {1.0}, 2.0, 1e-10, 1e-12);
        std::printf("RK45 on y' = -2ty: %d steps, error %.2e\n", r.steps, std::fabs(r.y[0] - std::exp(-4.0)));
        CHECK_NEAR(r.y[0], std::exp(-4.0), 1e-9);
        CHECK_LESS(static_cast<double>(r.steps), 400.0);
    }
    return check::summary("rk4");
}
