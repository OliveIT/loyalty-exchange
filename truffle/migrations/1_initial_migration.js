var Migrations = artifacts.require("./Migrations.sol");
var LEToken        = artifacts.require("./LEToken.sol");


module.exports = function(deployer) {
  deployer.deploy(Migrations).then(function() {
    return deployer.deploy(LEToken);
  }).then((ans) => {
    return ans;
  })
};
